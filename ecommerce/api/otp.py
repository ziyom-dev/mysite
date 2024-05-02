from ..models import Otp
from django.utils import timezone
from datetime import timedelta
from .utils import send_telegram_message, send_otp_by_sms
from rest_framework_simplejwt.tokens import RefreshToken
from Customer.models import User
import random

def generate_otp(length=6):
    """Генерирует OTP заданной длины."""
    numbers = '0123456789'
    otp = ''.join(random.choice(numbers) for i in range(length))
    return otp

def send_otp(phone_number):
    try:
        # Проверяем, существует ли уже OTP для данного номера телефона
        otp, created = Otp.objects.get_or_create(phone_number=phone_number)
        if created:
            # Если объект создан, генерируем OTP код и сохраняем его
            otp.otp = generate_otp()
            otp.save()
        else:
            # Если объект уже существует, проверяем, прошло ли уже 60 секунд
            otp_time = otp.time if timezone.is_aware(otp.time) else timezone.make_aware(otp.time)
            elapsed_time = timezone.now() - otp_time
            if elapsed_time < timedelta(seconds=60):
                # Возвращаем оставшееся время до повторной отправки
                remaining_time = timedelta(seconds=60) - elapsed_time
                return {"success": False, "remaining_time": remaining_time.total_seconds()}
            else:
                # Если прошло больше 60 секунд, обновляем время создания старого OTP
                otp.attempts = 3
                otp.time = timezone.now()
                otp.otp = generate_otp()
                otp.save()
        
        # Здесь будет код для отправки OTP
        send_telegram_message(f'{phone_number}: {otp.otp}')
        send_otp_by_sms(phone_number, otp.otp)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_otp(phone_number, otp):
    try:
        # Получаем объект OTP для данного номера телефона
        otp_obj = Otp.objects.get(phone_number=phone_number)
        
        # Проверяем существует ли OTP для данного номера телефона
        if not otp_obj:
            return {"success": False, "message": "OTP not found for this phone number."}
        
        # Проверяем совпадение OTP
        if otp_obj.otp == otp:
            # Создаем или получаем пользователя
            user, created = User.objects.get_or_create(phone_number=phone_number, defaults={'username': phone_number})

            # Удаляем объект OTP
            otp_obj.delete()
            
            if created:
                send_telegram_message(f'Новый пользователь: {phone_number}')

            # Создаем JWT токены
            refresh = RefreshToken.for_user(user)
            return {"success": True, "message": "OTP verification successful.", "refresh": str(refresh), "access": str(refresh.access_token), "created": created}
        else:
            # Уменьшаем количество попыток при несовпадении OTP
            otp_obj.attempts -= 1
            if otp_obj.attempts <= 0:
                # Удаляем объект, если использованы все попытки
                otp_obj.delete()
                return {"success": False, "message": "Invalid OTP. Attempts limit reached. Send the request again!"}
            else:
                otp_obj.save()
                return {"success": False, "message": "Invalid OTP. Attempts left: {}".format(otp_obj.attempts)}
    
    except Otp.DoesNotExist:
        return {"success": False, "message": "OTP not found for this phone number."}


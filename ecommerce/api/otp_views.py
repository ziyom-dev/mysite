# otp_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Customer.models import User
from .otp_service import send_otp, verify_otp, otp_storage
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError


# УДАЛИ ПОТОМ НАХУЙ!!
class OTPStorageView(APIView):
    def get(self, request):
        # Возвращаем содержимое otp_storage
        return Response([otp_storage])

class AuthView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")

        # Проверка на наличие номера телефона
        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Валидация номера телефона
        try:
            validate_international_phonenumber(phone_number)
        except ValidationError:
            return Response({"error": "Invalid phone number format."}, status=status.HTTP_418_IM_A_TEAPOT)
        
        # Если пользователь уже существует, отправляем OTP для входа
        result = send_otp(phone_number)
        if result["success"]:
            return Response({"message": f"OTP sent to {phone_number}.", "code": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        else:
            return Response({"timeout": result["timeout"]}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    def put(self, request):
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")

        # Проверка на наличие номера телефона и OTP
        if not phone_number or not otp:
            return Response({"error": "Phone number and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка OTP
        result = verify_otp(phone_number, otp)
        
        if result["success"]:
            user, created = User.objects.get_or_create(phone_number=phone_number, defaults={'username': phone_number})
            
            # Создание JWT токенов
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'created': created,
            }, status=status.HTTP_200_OK)
        elif result["error_code"] == 429:
            return Response({"timeout": result["timeout"]}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        else:
            return Response({"error": result['error_code']}, status=status.HTTP_400_BAD_REQUEST)
        

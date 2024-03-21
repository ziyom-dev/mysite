# otp_service.py

import random
import time
import requests

# Словарь для хранения OTP в памяти
otp_storage = {}


TELEGRAM_TOKEN = '7056099882:AAEKKwskPJk5NZ4pcQ2a20Xh2fYZKc0YSP0'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'


def generate_otp(length=6):
    """Генерирует OTP заданной длины."""
    numbers = '0123456789'
    otp = ''.join(random.choice(numbers) for i in range(length))
    return otp

def send_otp_via_telegram(chat_id, message):
    """
    Отправляет сообщение через Telegram бота.
    
    :param chat_id: ID чата в Telegram, куда будет отправлено сообщение.
    :param message: Текст сообщения для отправки.
    """
    data = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.post(TELEGRAM_API_URL, data=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения через Telegram: {e}")
        return False

def send_otp(phone_number, timeout=60, attempts=1):
    current_time = time.time()
    attempts_info = otp_storage.get(phone_number, {"otp": "", "send_attempts": 0, "last_send_attempt_time": 0, "verify_attempts": 0, "last_verify_attempt_time": 0})
    # Проверяем, не превышено ли количество попыток
    if attempts_info["send_attempts"] >= attempts and (current_time - attempts_info["last_send_attempt_time"]) < timeout:
        # Возвращаем результат с ошибкой
        return {"success": False, "timeout": timeout - round(current_time - attempts_info["last_send_attempt_time"])}

    # Увеличиваем счетчик попыток и обновляем время последней попытки
    attempts_info["send_attempts"] += 1
    attempts_info["last_send_attempt_time"] = current_time
    otp_storage[phone_number] = attempts_info
    
    """Генерирует и отправляет OTP, выводя его в консоль."""
    otp = generate_otp()
    otp_storage[phone_number]["otp"] = otp  # Сохранение OTP в словаре
    
    chat_id = "-4157512195"
    otp_message = f"{phone_number}: {otp}"
    
    telegram_sent_successfully = send_otp_via_telegram(chat_id, otp_message)
    if not telegram_sent_successfully:
        print("Не удалось отправить OTP через Telegram.")
    else:
        print(f"OTP для {phone_number} успешно отправлен через Telegram.")
    
    print(f"OTP for {phone_number}: {otp}")  # Вывод в консоль
    return {"success": True, "otp": otp}


def verify_otp(phone_number, otp, timeout=60, attempts=3):
    
    if phone_number not in otp_storage:
        return {"success": False, "error_code": 404}
    else: 
        current_time = time.time()
        attempts_info = otp_storage.get(phone_number, {"otp": "", "send_attempts": 0, "last_send_attempt_time": 0, "verify_attempts": 0, "last_verify_attempt_time": 0})
        # Проверяем, не превышено ли количество попыток
        if attempts_info["verify_attempts"] >= attempts and (current_time - attempts_info["last_verify_attempt_time"]) < timeout:
            # Возвращаем результат с ошибкой
            return {"success": False, "error_code": 429, "timeout": timeout - round(current_time - attempts_info["last_verify_attempt_time"])}

        # Увеличиваем счетчик попыток и обновляем время последней попытки
        attempts_info["verify_attempts"] += 1
        attempts_info["last_verify_attempt_time"] = current_time
        otp_storage[phone_number] = attempts_info
        
        expected_otp = otp_storage[phone_number]["otp"]
        if expected_otp == otp:
            otp_storage.pop(phone_number, None)
            return {"success": True}
        return {"success": False, "error_code": 400, "timeout": timeout - round(current_time - attempts_info["last_verify_attempt_time"])}


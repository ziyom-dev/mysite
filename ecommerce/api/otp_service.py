# otp_service.py

import random
import time

# Словарь для хранения OTP в памяти
otp_storage = {}
send_otp_attempts = {}
verify_otp_attempts = {}


def generate_otp(length=6):
    """Генерирует OTP заданной длины."""
    numbers = '0123456789'
    otp = ''.join(random.choice(numbers) for i in range(length))
    return otp

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


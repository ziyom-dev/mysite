import requests
from django.conf import settings

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': settings.TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=data)
    return response.status_code == 200

def send_otp_by_sms(phone_number, otp):
    url = "https://notify.eskiz.uz/api/message/sms/send"
    data={
        'mobile_phone': f'{phone_number}',
        'message': f'Onmalika.uz\nВаш код: {otp}\nНикому не сообщайте ваш код авторизации!',
        'from': '4546',
    }
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTYxNDU4NTMsImlhdCI6MTcxMzU1Mzg1Mywicm9sZSI6InVzZXIiLCJzaWduIjoiYzVmMjJlZTQ0NzcyMmJiNzMzNTJiYWE4MjQ2ZDIyM2EyZTYyOThhYzM2NWMyODU0YzQ2OGVjMzg3ZDFlMzgxYiIsInN1YiI6IjcwNDkifQ.t95qoRKLKvI5JP2x247CeMQUZfCFcC0rNJ8xSOTU0gI'
    }

    response = requests.post(url, headers=headers, data=data)
    return response.status_code == 200

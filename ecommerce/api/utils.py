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
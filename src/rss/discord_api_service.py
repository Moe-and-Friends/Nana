import requests

from config import settings, RSS_WEBHOOKS
from typing import List


def send_webhooks(webhook_data: List):
    for url in settings.get(RSS_WEBHOOKS):
        requests.post(
            url,
            json={
                "embeds": webhook_data
            })

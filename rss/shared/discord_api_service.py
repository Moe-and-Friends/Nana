import requests

from .beautifulsoup_service import Metadata
from config import settings, RSS_WEBHOOKS
from discord import Message
from typing import List


def generate_webhook(message: Message, metadata: Metadata):
    author = message.author
    return {
        "author": {
            "name": metadata.site_name,
        },
        "color": metadata.colour,
        "description": metadata.description,
        "footer": {
            "icon_url": author.avatar.url,
            "text": author.name + " in " + "#" + message.channel.name + " @ " + message.guild.name,
        },
        "image": {
            "url": metadata.image,
        },
        "title": metadata.title,
        "url": metadata.url,
    }


def send_webhooks(webhook_data: List):
    for url in settings.get(RSS_WEBHOOKS):
        requests.post(
            url,
            json={
                "embeds": webhook_data
            })

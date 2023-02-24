
from .mangadex_api_service import Chapter, Manga
from discord import Message

def build_chapter_webhook(message: Message, chapter: Chapter, manga: Manga, url: str):
    author = message.author
    # TODO: migrate this to Webhook/Embed data class.
    return {
        "color": 15102792, # Mangadex yellow colour
        "footer": {
            "icon_url": author.avatar.url,
            "text": author.name + " in " + "#" + message.channel.name + " @ " + message.guild.name,
        },
        "image": {
            "url": chapter.preview_url,
        },
        "title": manga.title_en + " - " + "Chapter {}".format(chapter.chapter),
        "url": url,
    }

from .api_service import Chapter, Cover, Manga
from discord import Message

# TODO: The code in this file is fairly repetitive right now for simplify of development.

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
        "title": manga.title_en + " - " + "Chapter {}".format(chapter.chapter_num),
        "url": url,
    }

def build_manga_webhook_full(message: Message, manga: Manga):
    author = message.author
    # TODO: migrate this to Webhook/Embed data class.
    return {
        # TODO: Investigate using K-Means to generate a colour?
        "color": 15102793, # Mangadex yellow colour.
        "description": manga.description_en if len(manga.description_en) <= 350 else manga.description_en[:347] + "...",
        "footer": {
            "icon_url": author.avatar.url,
            "text": author.name + " in " + "#" + message.channel.name + " @ " + message.guild.name,
        },
        "image": {
           "url": manga.preview_url
        },
        "title": manga.title_en,
        "url": manga.url
    }

def build_manga_webhook_preview(message: Message, manga: Manga, cover: Cover):
    author = message.author
    # TODO: migrate this to Webhook/Embed data class.
    return {
        "color": 15102793, # Mangadex yellow colour.
        "description": manga.description_en if len(manga.description_en) <= 100 else manga.description_en[:97] + "...",
        "footer": {
            "icon_url": author.avatar.url,
            "text": author.name + " in " + "#" + message.channel.name + " @ " + message.guild.name,
        },
        "thumbnail": {
            "url": cover.url # TODO
        },
        "title": manga.title_en,
        "url": manga.url
    }

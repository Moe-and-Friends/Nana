
import requests

from typing import Dict

MANGADEX_API_URL = "https://api.mangadex.org"
MANGADEX_API_CHAPTER_PATH = MANGADEX_API_URL + "/chapter"
MANGADEX_API_MANGA_PATH = MANGADEX_API_URL + "/manga"
MANGADEX_OG_PREVIEW_URL = "https://og.mangadex.org/og-image/chapter/{uuid}"

class MangadexBase:

    def __init__(self, id: str = None):
        self._id = id

    @property
    def id(self):
        return self._id


class Chapter(MangadexBase):

    def __init__(self, id: str = None, chapter: str = None, manga_uuid: str = None, title: str = None):
        """
        Notes:
            - title is for the Chapter title, not the Manga title
        """
        super().__init__(id=id)
        self._chapter = chapter
        self._manga_uuid = manga_uuid
        self._title = title

    @property
    def chapter(self):
        if self._chapter == "null":
            return None
        return self._chapter
    
    @property
    def preview_url(self):
        return MANGADEX_OG_PREVIEW_URL.format(uuid = super().id)

    @property
    def title(self):
        if self._title == "null":
            return None
        return self._title

    @property
    def manga_uuid(self):
        return self._manga_uuid

    @classmethod
    def get_chapter_details(cls, id: str):

        # Immediate check for required arguments
        if id is None:
            return None

        res = requests.get(MANGADEX_API_CHAPTER_PATH, params={"ids[]": [id]})
        try:
            if res.status_code == 200:
                jsonRes = res.json()

                # Expect one response in the data field
                chapter_data = jsonRes["data"][0]
                chapter_attributes = chapter_data.get("attributes", dict())
                chapter_relations = chapter_data.get("relationships", dict())

                return Chapter(
                    id=chapter_data.get("id", str()),
                    chapter=chapter_attributes.get("chapter", "error"),
                    # Gets the ID from the relationship of type "manga".
                    manga_uuid=[c.get("id", None) for c in chapter_relations if c.get("type") == "manga"][0],
                    title=chapter_attributes.get("title", "error")
                )

            else:
                raise Exception()
        except Exception:
            return None


class Manga(MangadexBase):

    def __init__(self, id: str = None, title: Dict[str, str] = dict()):
        super().__init__(id=id)
        self._title = title

    @property
    def title(self):
        return self._title

    @property
    def title_en(self):
        return self._title.get("en", "Unknown Title")

    @classmethod
    def get_manga_details(cls, id: str):
        res = requests.get(MANGADEX_API_MANGA_PATH + "/" + id)
        try:
            if res.status_code == 200:
                jsonRes = res.json()

                manga_data = jsonRes["data"]
                manga_attributes = manga_data.get("attributes")

                return Manga(
                    id=manga_data.get("id", str()),
                    title=manga_attributes.get("title")
                )
            else:
                raise Exception()
        except:
            return None


import requests

from typing import Dict, List

MANGADEX_API_URL = "https://api.mangadex.org"
MANGADEX_API_CHAPTER_PATH = MANGADEX_API_URL + "/chapter"
MANGADEX_API_COVER_PATH = MANGADEX_API_URL + "/cover/{uuid}"
MANGADEX_API_MANGA_PATH = MANGADEX_API_URL + "/manga"
MANGADEX_COVER_PATH = "https://uploads.mangadex.org/covers/{manga_id}/{cover_filename}"
MANGADEX_MANGA_PATH = "https://mangadex.org/title/{uuid}"
MANGADEX_OG_CHAPTER_PREVIEW_URL = "https://og.mangadex.org/og-image/chapter/{uuid}"
MANGADEX_OG_MANGA_PREVIEW_URL = "https://og.mangadex.org/og-image/manga/{uuid}"

class MangadexBase:

    def __init__(self, id: str = None):
        self._id = id

    @property
    def id(self):
        return self._id


class Chapter(MangadexBase):

    def __init__(self, id: str = None, chapter_num: str = None, manga_uuid: str = None, title: str = None):
        """
        Notes:
            - title is for the Chapter title, not the Manga title
        """
        super().__init__(id=id)
        self._chapter_num = chapter_num
        self._manga_uuid = manga_uuid
        self._title = title

    @property
    def chapter_num(self):
        if self._chapter_num == "null":
            return ""
        return self._chapter_num

    @property
    def preview_url(self):
        return MANGADEX_OG_CHAPTER_PREVIEW_URL.format(uuid = super().id)

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

        #res = requests.get(MANGADEX_API_CHAPTER_PATH, params={"ids[]": [id]})
        res = requests.get(MANGADEX_API_CHAPTER_PATH + "/" + id)
        try:
            if res.status_code == 200:
                jsonRes = res.json()

                # Expect one response in the data field
                #chapter_data = jsonRes["data"][0]
                res_chapter_data = jsonRes.get("data", dict())
                res_chapter_attributes = res_chapter_data.get("attributes", dict())
                res_chapter_relations = res_chapter_data.get("relationships", dict())

                chapter_id = res_chapter_data.get("id", str())
                chapter_num = res_chapter_attributes.get("chapter", "error_occured")
                chapter_title = res_chapter_attributes.get("title", "error_occured")

                chapter_manga_uuid = str()
                for rel in res_chapter_relations:
                    if rel.get("type") == "manga":
                        chapter_manga_uuid = rel.get("id", str())
                        break

                return Chapter(
                    id = chapter_id,
                    chapter_num = chapter_num,
                    manga_uuid = chapter_manga_uuid,
                    title = chapter_title
                )

            else:
                raise Exception()
        except Exception:
            return None


class Manga(MangadexBase):

    NO_DESCRIPTION_AVAILABLE = "No description available."

    def __init__(self,
                 id: str = None,
                 cover_arts: List[str] = list(),
                 description: str = str(),
                 title: Dict[str, str] = dict()):
        super().__init__(id=id)
        self._cover_arts = cover_arts
        self._description = description
        self._title = title

    @property
    def cover_arts(self):
        return self._cover_arts

    @property
    def description(self):
        if not self._description:
            return {"en": self.NO_DESCRIPTION_AVAILABLE}
        return self._description

    @property
    def description_en(self):
        return self._description.get("en", self.NO_DESCRIPTION_AVAILABLE)

    @property
    def preview_url(self):
        return MANGADEX_OG_MANGA_PREVIEW_URL.format(uuid = super().id)

    @property
    def title(self):
        return self._title

    @property
    def title_en(self):
        return self._title.get("en", "Unknown English Title")

    @property
    def url(self):
        return MANGADEX_MANGA_PATH.format(uuid = super().id)

    @classmethod
    def get_manga_details(cls, id: str):
        res = requests.get(MANGADEX_API_MANGA_PATH + "/" + id)
        try:
            if res.status_code == 200:
                jsonRes = res.json()

                res_manga_data = jsonRes["data"]
                res_manga_attributes = res_manga_data.get("attributes", dict())
                res_manga_relationships = res_manga_data.get("relationships", list())

                cover_arts = [c.get("id") for c in res_manga_relationships if c.get("type") == "cover_art"]

                return Manga(
                    id=res_manga_data.get("id", str()),
                    cover_arts=cover_arts,
                    description=res_manga_attributes.get("description", dict()),
                    title=res_manga_attributes.get("title")
                )
            else:
                raise Exception()
        except:
            return None

class Cover(MangadexBase):

    def __init__(self, id: str = None, filename: str = str(), manga_id: str = str()):
        super().__init__(id=id) # ID is the ID of whatever container object is creating this Cover
        self._filename = filename
        self._manga_id = manga_id

    @property
    def filename(self):
        return self._filename

    @property
    def manga_id(self):
        return self._manga_id

    @property
    def url(self):
        return MANGADEX_COVER_PATH.format(manga_id = self._manga_id,
                                          cover_filename = self._filename)

    @classmethod
    def get_cover_details(cls, cover_id: str = None):
        res = requests.get(MANGADEX_API_COVER_PATH.format(uuid=cover_id))
        try:
            if res.status_code == 200:
                jsonRes = res.json()

                res_cover_data = jsonRes['data']
                res_cover_attributes = res_cover_data.get("attributes", dict())
                res_cover_relationships = res_cover_data.get("relationships", list())

                manga_id = str()
                for rel in res_cover_relationships:
                    if rel.get("type") == "manga":
                        manga_id = rel.get("id")
                        break

                return Cover(
                    id = cover_id,
                    filename = res_cover_attributes.get("fileName", str()),
                    manga_id = manga_id
                )

            else:
                raise Exception()
        except Exception as e:
            return None


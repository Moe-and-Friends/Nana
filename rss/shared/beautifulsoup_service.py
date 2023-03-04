
import requests

from bs4 import BeautifulSoup
from retry import retry

SPOOF_DISCORD_USER_AGENT = "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)"


class Metadata:

    def __init__(self,
                 description: str = None,
                 image: str = None,
                 site_name: str = None,
                 title: str = None,
                 url: str = None):

        self._description = description
        self._image = image
        self._site_name = site_name
        self._title = title
        self._url = url

    @property
    def description(self):
        return self._description

    @property
    def image(self):
        return self._image

    @property
    def site_name(self):
        return self._site_name

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url


def fetch_page_metadata(url: str, spoof_user_agent: bool = True):
    """
    Fetches OpenGraph metadata from websites for rendering in Discord embeds.
    """

    @retry(tries=3, delay=2)
    def fetch(url: str, session: requests.Session):
        return session.get(url)

    def get_og_meta_property(soup: BeautifulSoup, property: str):
        meta_property = soup.find("meta", property=property)
        if property := meta_property.get("content"):
            return property
        return meta_property.get("name")

    def get_title(soup: BeautifulSoup):
        if title := soup.title:
            return title.string
        return get_og_meta_property(soup, "og:title")

    session = requests.Session()
    if spoof_user_agent:
        session.headers.update({'User-Agent': SPOOF_DISCORD_USER_AGENT})

    page = fetch(url, session)
    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.text, 'html.parser')

    # Start to fetch metadata
    og_description = get_og_meta_property(soup, "og:description")
    og_image = get_og_meta_property(soup, "og:image:secure_url")
    if not og_image:
        og_image = get_og_meta_property(soup, "og:image")
    og_site_name = get_og_meta_property(soup, "og:site_name")
    og_title = get_title(soup)
    og_url = get_og_meta_property(soup, "og:url")

    return Metadata(
        description=og_description,
        image=og_image,
        site_name=og_site_name,
        title=og_title,
        url=og_url
    )

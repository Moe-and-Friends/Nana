
import requests

from bs4 import BeautifulSoup
from retry import retry

SPOOF_DISCORD_USER_AGENT = "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)"


class Metadata:

    def __init__(self,
                 colour: int = 0,
                 description: str = None,
                 image: str = None,
                 site_name: str = None,
                 soup: BeautifulSoup = None,
                 title: str = None,
                 url: str = None):

        self._colour: int = colour
        self._description: str = description
        self._image: str = image
        self._site_name: str = site_name
        self._soup: BeautifulSoup = soup
        self._title: str = title
        self._url: str = url

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def site_name(self):
        return self._site_name

    @site_name.setter
    def site_name(self, value):
        self._site_name = value

    @property
    def soup(self):
        return self._soup

    # No setter for BeautifulSoup

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value


def fetch_page_metadata(url: str, spoof_user_agent: bool = True):
    """
    Fetches OpenGraph metadata from websites for rendering in Discord embeds.
    """

    @retry(tries=3, delay=2)
    def fetch(url: str, session: requests.Session):
        return session.get(url)

    def get_meta_property(soup: BeautifulSoup, property: str, alt_property: str = None):

        # Inner function to handle actually fetching the property itself from Soup.
        def _get_meta_property(soup: BeautifulSoup, property: str):
            # Usually, meta links are categorised by property.
            meta_property = soup.find("meta", property=property)
            if meta_property:
                if content := meta_property.get("content"):
                    return content

            # Sometimes, meta links are instead categorised by name
            meta_name = soup.find("meta", attrs={'name': property})  # Name has to be set via attrs
            if meta_name:
                if content := meta_name.get("content"):
                    return content

            return None

        # Try to get the meta value using the primary property name, if specified.
        if property_from_primary := _get_meta_property(soup, property):
            return property_from_primary
        # Try to get the meta value using the alternative property name, if specified.
        elif alt_property:
            if property_from_alt := _get_meta_property(soup, alt_property):
                return property_from_alt
        # If both fail, explicitly return None.
        else:
            return None

    def get_title(soup: BeautifulSoup):
        if title := soup.title:
            return title.string
        return get_meta_property(soup, "og:title")

    session = requests.Session()
    if spoof_user_agent:
        session.headers.update({'User-Agent': SPOOF_DISCORD_USER_AGENT})

    page = fetch(url, session)
    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.text, 'html.parser')

    # Start to fetch metadata

    # Special handling for colour
    site_colour = 0
    if colour := get_meta_property(soup, "theme-color"):
        if colour and colour.startswith("#"):
            site_colour = int(colour[1:], base=16)

    og_description = get_meta_property(soup, "og:description", "description")
    og_image = get_meta_property(soup, "og:image:secure_url", "og:image")
    og_site_name = get_meta_property(soup, "og:site_name")
    og_title = get_title(soup)
    og_url = get_meta_property(soup, "og:url")
    if not og_url:
        og_url = url  # Fallback to the originally provided URL in the message.

    return Metadata(
        colour=site_colour,
        description=og_description,
        image=og_image,
        site_name=og_site_name,
        soup=soup,
        title=og_title,
        url=og_url
    )

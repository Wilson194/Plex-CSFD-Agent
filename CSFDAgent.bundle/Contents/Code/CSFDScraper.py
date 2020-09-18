import datetime
import re
import unicodedata, re

POSTERS_RE = r'background-image:\s*url\s*\(.*//(.*)\?h[0-9]*.*'
ACTOR_ID_RE = r'/tvurce/([0-9]+)-.*'
FILM_ID_RE = r'/film/([0-9]+)-[^/]*/(?:([0-9]+)-[^/]*)*'


def strip_diacritics(s):
    """
      Removes diacritics from a given string.
    """
    u = unicode(s).replace(u"\u00df", u"ss").replace(u"\u1e9e", u"SS")
    nkfd_form = unicodedata.normalize('NFKD', u)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii


class CSFDID:
    def __init__(self):
        self.primary_id = None
        self.secondary_id = None


class CSFDMetadata:
    def __init__(self):
        self.id = None
        self.primary_name = None
        self.other_names = []
        self.genres = []
        self.origin = []
        self.year = None
        self.duration = None
        self.tags = []
        self.rating = None
        self.release_date = None
        self.summary = None
        self.writers = []
        self.directors = []
        self.producers = []
        self.actors = []
        self.posters = []

        self.merged_name = None


class CSFDPerson:
    def __init__(self, person_id, name=None, role=None, image=None):
        self.id = person_id
        self.name = name
        self.role = role
        self.image = image


def scrape_film_metadata(data):
    csfd_meta = CSFDMetadata()

    # Test for serie
    result = data.xpath('//div[contains(@class, "episode")]')
    if result:  # TODO: Fix also eng name
        merged_name = data.xpath('//div[contains(@class, "series-navigation")]//a/text()')[0]

        csfd_meta.merged_name = merged_name

    # Primary name
    try:
        csfd_meta.primary_name = data.xpath('//h1[@itemprop="name"]/text()')[0].strip()
    except:
        pass

    # Other names
    try:
        csfd_meta.other_names = [x.strip() for x in data.xpath('//ul[@class="names"]//h3/text()')]
    except:
        pass

    # Genres
    try:
        csfd_meta.genres = [x.strip() for x in data.xpath('//p[@class="genre"]/text()')[0].split('/')]
    except:
        pass

    # Origin
    try:
        tokens = data.xpath('//p[@class="origin"]/text()[1]')
        csfd_meta.origin = [x.strip() for x in tokens[0].replace(',', '').split('/')]
    except:
        pass

    # Year
    try:
        csfd_meta.year = int(data.xpath('//span[@itemprop="dateCreated"]/text()')[0])
    except:
        pass

    # Length [milliseconds]
    try:
        duration_minutes = int(data.xpath('//p[@class="origin"]/text()[last()]')[0].replace(',', '').strip())
        csfd_meta.duration = duration_minutes * 60 * 1000
    except:
        pass

    # Tags
    try:
        csfd_meta.tags = [x.strip() for x in
                          data.xpath('//div[contains(@class, "tags")]//div[@class="content"]//a/text()')]
    except:
        pass

    # Rating [scale from 0 to 10]
    try:
        csfd_meta.rating = int(data.xpath('//div[@id="rating"]/h2/text()')[0].replace('%', '')) / 10.
    except:
        pass

    # Summary
    try:
        csfd_meta.summary = "".join(data.xpath('//div[@id="plots"]//div[@class="content"]//div//*/text() |'
                                               '//div[@id="plots"]//div[@class="content"]//div/text()')).strip()
    except:
        pass

    # Release data
    try:
        release_dates = [x.strip().split(' ')[0] for x in data.xpath('//div[@id="releases"]//td[@class="date"]/text()')]
        release_dates = [datetime.datetime.strptime(release_date, '%d.%m.%Y') for release_date in release_dates]
        csfd_meta.release_date = min(release_dates).date()
    except:
        pass

    # Posters
    try:
        posters = []
        posters_style = data.xpath('//div[@id="posters"]//div[@class="image"]/@style')
        for poster_style in posters_style:
            poster_url = re.search(POSTERS_RE, poster_style.replace('\\', '')).group(1)
            posters.append('http://' + poster_url)

        csfd_meta.posters = posters
    except:
        pass

    # Creators
    try:
        creators = {}
        creators_element = data.xpath('//div[@class="creators"]//h4')
        for creator in creators_element:
            creator_type = strip_diacritics(creator.xpath('text()')[0].replace(':', '').strip()).lower()
            # creator_names = creator.xpath('following-sibling::span/a/text()')
            for create_tag in creator.xpath('following-sibling::span/a/@href'):
                creator_id = re.search(ACTOR_ID_RE, create_tag).group(1)

                if creator_type in creators:
                    creators[creator_type].append(creator_id)
                else:
                    creators[creator_type] = []
                    creators[creator_type].append(creator_id)

        for person_id in creators.get('rezie', []):
            person = CSFDPerson(person_id)
            csfd_meta.directors.append(person)

        for person_id in creators.get('hraji', []):
            person = CSFDPerson(person_id)
            csfd_meta.actors.append(person)

        for person_id in creators.get('scenar', []):
            person = CSFDPerson(person_id)
            csfd_meta.writers.append(person)

        # for person_id in creators.get('kamera', []):
        #     person = CSFDPerson(person_id)
        #     csfd_meta.camera.append(person)
        #
        # for person_id in creators.get('hudba', []):
        #     person = CSFDPerson(person_id)
        #     csfd_meta.music.append(person)

        for person_id in creators.get('producenti', []):
            person = CSFDPerson(person_id)
            csfd_meta.producers.append(person)

    except:
        pass

    return csfd_meta


def scrape_search_results(data):
    urls = data.xpath(
        '//div[@id="search-films"]//ul[contains(@class, "ui-image-list")]//a[contains(@class, "film")]/@href')

    results = []
    for url in urls:
        result = CSFDID()
        re_result = re.search(FILM_ID_RE, url)
        result.primary_id = re_result.group(1)
        result.secondary_id = re_result.group(2)
        results.append(result)

    return results


def scrape_actor_results(data):
    name = data.xpath('//div[@id="profile"]//h1/text()')[0].strip()
    image = data.xpath('//div[@id="profile"]//div[@class="image"]//img/@src')[0].replace('//', 'http://')

    href = data.xpath('//div[@class="navigation"]//li[contains(@class, "biography")]//a/@href')[0]
    person_id = re.search(ACTOR_ID_RE, href).group(1)

    return CSFDPerson(person_id, name, '', image)



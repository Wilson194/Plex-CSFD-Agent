# -*- coding: utf-8 -*-
# encoding: utf-8
import re

from Containers import MovieSearchResult, Movie, Person

BASE_URL = "http://www.csfd.cz"


def _convert_flag(flag_url):
    _MAP_FLAG_ISO = {
        1: 'US',  # USA
        2: 'GB',  # Velká Británie
        3: 'AU',  # Austrálie
        4: 'DE',  # Německo
        5: 'AT',  # Rakousko
        6: 'CA',  # Kanada
        7: 'DK',  # Dánsko
        8: 'FI',  # Finsko
        10: 'HU',  # Maďarsko
        11: 'NL',  # Nizozemí
        12: 'PL',  # Polsko
        13: 'RU',  # Rusko
        14: 'SE',  # Švédsko
        15: 'CH',  # Švýcarsko
        16: 'TH',  # Thajsko
        17: 'TR',  # Turecko
        18: 'BE',  # Belgie
        19: 'FR',  # Francie
        21: 'IE',  # Irsko
        22: 'IT',  # Itálie
        23: 'ES',  # Španělština
        25: 'NO',  # Norsko
        27: 'AR',  # Argentina
        30: 'PT',  # Portugalsko
        31: 'TJ',  # Tádžikistán
        33: 'JP',  # Japonsko
        34: 'CZ',  # Česká Republika
        35: 'AU',  # Austrálie
        36: 'CZ',  # Česká Republika
        37: 'BG',  # Bulharsko
        41: 'EG',  # Egypt
        47: 'DE',  # Německo
        48: 'DE',  # Německo
        49: 'CN',  # Čína
        52: 'SK',  # Slovensko
        55: 'PE',  # Peru
        62: 'IS',  # Island
        # TODO
    }
    _RE_FLAG_NUM = re.compile("_([0-9]+)")

    flag_num = int(_RE_FLAG_NUM.search(flag_url).group(1))

    try:
        return _MAP_FLAG_ISO[flag_num]
    except KeyError:
        return '-'


def parse_search_result(root, add_others=False):
    results = list()

    try:
        doc_movies = root.xpath("//div[@id='search-films']/div[1]")[0]
    except IndexError:
        return results

    # nalezené filmy - první výsledky
    for item in doc_movies.xpath("ul[1]/li"):
        a = item.find("div/h3/a")

        # český název
        name = a.text

        # URL stránky filmu
        url = BASE_URL + a.get('href')
        url += 'prehled/'

        # barva podle hodnocení
        color = a.get('class')

        # druhý název (většinou původní název filmu)
        try:
            name_alt = item.xpath("span[@class='search-name']/text()")[0].strip('()')
        except IndexError:
            name_alt = ""

        # žánry (nejsou všechny), země, rok
        gcy = item.find("div/p").text

        # rok vydání
        try:
            year = int(gcy.split(',')[-1].strip())
        except ValueError:
            year = None

        results.append(MovieSearchResult(name, name_alt, year, url))

    if add_others:
        # nalezené filmy - další výsledky
        for item in doc_movies.xpath("ul[2]/li"):
            a = item.find("a")

            # český název
            name = a.text

            # URL stránky filmu
            url = BASE_URL + a.get('href')

            # barva podle hodnocení
            color = a.get('class')

            # druhý název (většinou původní název filmu)
            try:
                name_alt = item.xpath("span[@class='search-name']/text()")[0].strip('()')
            except IndexError:
                name_alt = ""

            # rok vydání
            year = int(item.xpath("span[@class='film-year']/text()")[0].strip('()'))

            results.append(MovieSearchResult(name, name_alt, year, url))

    return results


def parse_movie(root):
    container = Movie()

    # ID
    url = root.xpath('//head/link[@rel="canonical"]')[0].get('href')
    id_re = re.compile('http.*/film/([0-9]*).*/.*')
    csfd_id = id_re.search(url).group(1)
    container.id = csfd_id

    # Film section info
    profile = root.xpath("//div[@id='profile']/div/div[@class='info']")[0]

    # Film type
    try:
        container.type = profile.xpath('div/h1/span/text()')[0].strip('()')
    except:
        pass

    # Official CZ name
    container.names['CZ'] = profile.xpath("div/h1/text()")[0].strip()

    # Other names in different languages
    for item in profile.xpath("ul[@class='names']/li"):
        country = item.find('img').get('alt')
        # Use only first name from the country
        if country in container.names:
            continue
        container.names[country] = item.find('h3').text.strip()

    # Genres
    raw_genres = profile.xpath("p[@class='genre']/text()")
    if raw_genres:
        container.genres = list(i.strip() for i in raw_genres[0].split('/'))

    # Duration
    try:
        duration_minutes = int(
            root.xpath('//p[@class="origin"]/text()[last()]')[0].replace(',', '').replace('min', '').strip())
        container.runtime = duration_minutes
    except:
        pass

    # Year
    try:
        container.year = int(root.xpath('//span[@itemprop="dateCreated"]/text()')[0])
    except:
        pass

    # Country
    try:
        raw_cyr = profile.xpath("p[@class='origin']/text()")[0]
        cyr = list(i.strip() for i in raw_cyr.split(','))

        # countries
        container.countries = list(i.strip() for i in cyr.pop().split('/'))

    except IndexError:
        pass

    # directors
    for item in profile.xpath(u"div[@class='creators']/div[h4='Režie:']//a"):
        person = Person(item.text, BASE_URL + item.get('href'))
        container.directors.append(person)

    # music
    for item in profile.xpath("div[@class='creators']/div[h4='Hudba:']//a"):
        person = Person(item.text, BASE_URL + item.get('href'))
        container.music.append(person)

    # actors
    for item in profile.xpath(u"div[@class='creators']/div[h4='Hrají:']//a"):
        person = Person(item.text, BASE_URL + item.get('href'))
        container.actors.append(person)

    # content
    try:
        container.content = "".join(root.xpath('//div[@id="plots"]//div[@class="content"]//div//*/text() |'
                                               '//div[@id="plots"]//div[@class="content"]//div/text()')).strip()
    except:
        pass

    # Rating section
    doc_rating = root.xpath("//div[@id='rating']")[0]

    # Rating
    try:
        rating = doc_rating.xpath("h2/text()")[0].strip('%')
        container.rating = int(rating)
    except IndexError:
        pass

    # Best film position
    try:
        rank = doc_rating.xpath("//a[contains(@href, '. nejlepsi')]/text()")[0]
        container.best_rank = int(rank.split('.')[0])
    except IndexError:
        pass

    # Wort film position
    try:
        rank = doc_rating.xpath("//a[contains(@href, '. nejhorsi')]/text()")[0]
        container.worst_rank = int(rank.rsplit('.')[0])
    except IndexError:
        pass

    # Best favourite position
    try:
        rank = doc_rating.xpath("//a[contains(@href, '. nejoblibenejsi')]/text()")[0]
        container.favorite_rank = int(rank.split('.')[0])
    except IndexError:
        pass

    # Best controversial rank
    try:
        rank = doc_rating.xpath("//a[contains(@href, '. nejrozporuplnejsi')]/text()")[0]
        container.controversial_rank = int(rank.split('.')[0])
    except IndexError:
        pass

    # All posters
    regexp = re.compile("url\('(.*)'")
    for raw in root.xpath("//div[@id='posters']/div[2]//div/@style"):
        link = regexp.search(raw).group(1).replace('\\', '')
        container.posters.append(link)

    if (len(container.posters) == 0):
        try:
            container.posters.append(root.xpath("//div[@id='poster']/img/@src")[0])
        except IndexError:
            pass

    # Link to IMDb.com
    try:
        container.imdb_url = root.xpath("//div[@id='share']//a[@title='profil na IMDb.com']/@href")[0]
    except IndexError:
        pass

    # Link to official web page
    try:
        container.website_url = root.xpath("//div[@id='share']//a[@class='www']/@href")[0]
    except IndexError:
        pass

    return container

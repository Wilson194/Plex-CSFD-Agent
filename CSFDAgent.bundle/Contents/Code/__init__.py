import CSFDScraper
from AgentMethods import *

# End run environment

CSFD_DETAIL_URL = "http://www.csfd.cz/film/{}"
CSFD_SEARCH_URL = "http://www.csfd.cz/hledat/?q={}"
CSDF_PERSON_URL = "https://www.csfd.cz/tvurce/{}"


def Start():
    HTTP.CacheTime = CACHE_1DAY


class CSFDAgent(Agent.Movies):
    name = 'CSFD Agent'
    languages = [Locale.Language.English]
    primary_provider = True
    fallback_agent = False
    accepts_from = None
    contributes_to = None


    def search(self, results, media, lang, manual=False):
        Log.Info('-' * 157)
        Log.Info('Start searching with CSFD Agent')
        Log.Info('-' * 157)

        name = resolve_film_name(media.filename, media.name)

        Log.Info('Resolving file with Name: {}, Year: {}, Duration{}'.format(name, media.year, media.duration))

        search_results = find_movie(name, media.year, media.duration, manual)

        for metadata, score in search_results:
            name = metadata.name['CZ']
            # TODO: Add other names

            results.Append(MetadataSearchResult(id=metadata,
                                                name=name,
                                                year=metadata.year,
                                                score=score,
                                                lang=Locale.Language.Czech))

        return


    def update(self, metadata, media, lang):
        Log.Info('-' * 157)
        Log.Info('Start updating with CSFD Agent')
        Log.Info('-' * 157)

        Log.Debug('Primary name: {}'.format(metadata.primary_name))
        if metadata.primary_name:
            metadata.title = metadata.primary_name

        Log.Debug('Year: {}'.format(metadata.year))
        if metadata.year:
            metadata.year = metadata.year

        Log.Debug('rating: {}'.format(metadata.rating))
        if metadata.rating:
            metadata.rating = metadata.rating

        Log.Debug('summary: {}'.format(metadata.summary))
        if metadata.summary:
            metadata.summary = metadata.summary

        Log.Debug('genres: {}'.format(metadata.genres))
        if metadata.genres:
            metadata.genres.clear()
            for genre in metadata.genres:
                metadata.genres.add(genre)

        Log.Debug('duration: {}'.format(metadata.duration))
        if csfd_metadata.duration:
            metadata.duration = metadata.duration

        Log.Debug('Tags: {}'.format(metadata.tags))
        if metadata.tags:
            metadata.tags.clear()
            for tag in metadata.tags:
                metadata.tags.add(tag)

        # Actors
        Log.Debug('actors: {}'.format(metadata.actors))
        if metadata.actors:
            metadata.roles.clear()
            for actor in metadata.actors:
                role = metadata.roles.new()
                person_metadata = self.csfd_person_metadata(actor.id)
                role.name = person_metadata.name
                role.photo = person_metadata.image

        Log.Debug('directors: {}'.format(metadata.directors))
        if metadata.directors:
            metadata.directors.clear()
            for director in metadata.directors:
                metadata.directors.add(director)

        Log.Debug('Posters: {}'.format(metadata.posters))
        if metadata.posters:
            for i, poster_url in enumerate(metadata.posters):
                poster = HTTP.Request(poster_url + '?h180')
                # metadata.posters[poster_url] = Proxy.Preview(poster, sort_order=i + 1)

        return

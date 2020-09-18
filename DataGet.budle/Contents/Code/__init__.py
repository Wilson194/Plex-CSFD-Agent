import os


def Start():
    HTTP.CacheTime = CACHE_1DAY


class DataGetAgent(Agent.Movies):
    name = 'DataGet'
    languages = [Locale.Language.English]
    primary_provider = True
    fallback_agent = False
    accepts_from = None
    contributes_to = None


    def search(self, results, media, lang, manual=False):
        output_file = os.path.abspath('/tmp/data.csv')

        text = str(media.filename) + ';' + str(media.name) + ';' + str(media.year) + ';' + str(
            media.duration) + '\n'
        Log.Info('==>' + text)


    def update(self, metadata, media, lang):
        pass

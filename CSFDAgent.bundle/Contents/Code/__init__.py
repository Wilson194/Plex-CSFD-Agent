import re


def Start():
    HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers[
        'User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'


class CSFDAgent(Agent.Movies):
    name = 'CSFD Agent'
    languages = [Locale.Language.English]
    primary_provider = True
    fallback_agent = False
    accepts_from = None
    contributes_to = None


    def search(self, results, media, lang, manual=False):
        Log('-' * 157)
        Log('Start searching with CSFD Agent')
        Log('-' * 157)

        return


    def update(self, metadata, media, lang):
        Log('-' * 157)
        Log('Start updating with CSFD Agent')
        Log('-' * 157)

        return

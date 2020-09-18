import re
import string
import sys
import urllib2
from StringIO import StringIO

import requests
from lxml import etree
import unicodedata


def clean_up_string(s):
    s = unicode(s)

    # Ands.
    s = s.replace('&', 'and')

    # Pre-process the string a bit to remove punctuation.
    s = re.sub('[' + string.punctuation + ']', '', s)

    # Lowercase it.
    s = s.lower()

    # Strip leading "the/a"
    s = re.sub('^(the|a) ', '', s)

    # Spaces.
    s = re.sub('[ ]+', ' ', s).strip()

    return s


def levenshtein_distance(first, second):
    first = clean_up_string(first)
    second = clean_up_string(second)

    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
        distance_matrix[i][0] = i
    for j in range(second_length):
        distance_matrix[0][j] = j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i - 1][j] + 1
            insertion = distance_matrix[i][j - 1] + 1
            substitution = distance_matrix[i - 1][j - 1]
            if first[i - 1] != second[j - 1]:
                substitution = substitution + 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length - 1][second_length - 1]


class String:

    @staticmethod
    def LevenshteinRatio(first, second):
        if len(first) == 0 or len(second) == 0:
            return 0.0
        else:
            return 1 - (levenshtein_distance(first, second) / float(max(len(first), len(second))))


    @staticmethod
    def Quote(target):
        return urllib2.quote(target)


    @staticmethod
    def Unquote(target):
        return urllib2.unquote(target)


    @staticmethod
    def Clean(s, form='NFKD', lang=None, strip_diacritics=False, strip_punctuation=False):

        # Guess at a language-specific encoding, should we need one.
        encoding_map = {'ko': 'cp949'}

        # Precompose.
        try:
            s = unicodedata.normalize(form, s.decode('utf-8'))
        except:
            try:
                s = unicodedata.normalize(form, s.decode(sys.getdefaultencoding()))
            except:
                try:
                    s = unicodedata.normalize(form, s.decode(sys.getfilesystemencoding()))
                except:
                    try:
                        s = unicodedata.normalize(form, s.decode('utf-16'))
                    except:
                        try:
                            s = unicodedata.normalize(form, s.decode(encoding_map.get(lang, 'ISO-8859-1')))
                        except:
                            try:
                                s = unicodedata.normalize(form, s)
                            except Exception, e:
                                pass

        # Strip control characters. No good can come of these.
        s = u''.join([c for c in s if not unicodedata.category(c).startswith('C')])

        # Strip punctuation if we were asked to.
        if strip_punctuation:
            s = u''.join([c for c in s if not unicodedata.category(c).startswith('P')])

        # Strip diacritics if we were asked to.
        if strip_diacritics:
            s = u''.join([c for c in s if not unicodedata.combining(c)])

        return s


    @staticmethod
    def StripDiacritics(s):
        """
          Removes diacritics from a given string.
        """
        u = unicode(s).replace(u"\u00df", u"ss").replace(u"\u1e9e", u"SS")
        nkfd_form = unicodedata.normalize('NFKD', u)
        only_ascii = nkfd_form.encode('ASCII', 'ignore')
        return only_ascii


class HTTP:
    class Wrapper:
        def __init__(self, r):
            self.r = r


        @property
        def content(self):
            return self.r

    @staticmethod
    def Request(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        result = requests.get(url, headers=headers)
        html = result.content
        return HTTP.Wrapper(html)


class HTML:
    @staticmethod
    def ElementFromString(web_page):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(web_page), parser)
        return tree


class Log:
    @staticmethod
    def Info(text):
        print text
        pass


    @staticmethod
    def Debug(text):
        # print text
        pass

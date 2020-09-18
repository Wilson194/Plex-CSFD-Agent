# -*- coding: utf-8 -*-
# encoding: utf-8


class Movie(object):
    def __init__(self):
        self.id = None
        self.actors = list()
        self.best_rank = None
        self.content = None
        self.controversial_rank = None
        self.countries = list()
        self.directors = list()
        self.favorite_rank = None
        self.genres = list()
        self.imdb_url = None
        self.music = list()
        self.names = {}
        self.posters = list()
        self.rating = None
        self.runtime = None
        self.url = None
        self.website_url = None
        self.worst_rank = None
        self.year = None
        self.type = None


    def __eq__(self, other):
        return other.id == self.id


    def __hash__(self):
        return hash(self.id)


    def __repr__(self):
        return self.names['CZ']


class MovieSearchResult(object):
    def __init__(self, name, name_alt, year, url):
        self.name = name
        self.name_alt = name_alt
        self.url = url
        self.year = year


class Person(object):
    def __init__(self, name, profile_url):
        self.name = name
        self.profile_url = profile_url

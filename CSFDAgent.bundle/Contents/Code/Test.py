# -*- coding: utf-8 -*-
# encoding: utf-8
import csv
import multiprocessing as mp

from AgentMethods import *


class Media:
    def __init__(self, name, year, duration, filename):
        self.name = name
        self.year = year
        self.duration = duration
        self.filename = filename


def search(media, manual=False):
    name = resolve_film_name(media.filename, media.name)
    search_results = find_movie(name, media.year, media.duration, manual)
    res = []
    for metadata, score in search_results:
        name = metadata.names['CZ']

        res.append([metadata.id, metadata.url, name, metadata.year, score])

    return res



def worker(row):
    results = search(Media(row[1], row[2], row[3], row[0]))

    if row[4] != results[0][0]:
        print 'BAD - ', row[0], results[0][0], row[4]
    else:
        print 'CORRECT', results[0][4]


if __name__ == '__main__':
    with open('D:\Programovani\Plex-CSFD-Agent\RunEnvironment\data.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=';')

        # row = list(csv_reader)[122]
        # results = search(Media(row[1], row[2], row[3], row[0]))


        pool = mp.Pool(20)
        for i in pool.map(worker, csv_reader):
            pass

        pool.close()
        pool.join()


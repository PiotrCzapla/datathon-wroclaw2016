#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import sys
import csv
import json
import numpy
from polyglot.text import Text, Word


def add_vote(dic, proj, age):
  try:
    dic[proj].append(int(age))
  except:
    dic[proj] = []
    dic[proj].append(int(age))


votes2015 = {}
votes2016 = {}


with open('data/votes_2015_encodingfix.csv', 'r') as csvvotes:
  reader = csv.reader(csvvotes, delimiter=';')
  for row in reader:
    #2015
    #Lp;Data;Wiek;Plec;Osiedle;Kod_Pocztowy;Zrodlo;Prog_1;Prog_2;Prog_3
    add_vote(votes2015, row[7], row[2])
    add_vote(votes2015, row[8], row[2])
    add_vote(votes2015, row[9], row[2])


with open('data/2016-12-03-WBO_lista_glosow_2016.csv', 'r') as csvvotes:
  reader = csv.reader(csvvotes, delimiter=';')
  for row in reader:
    #2016
    # Lp;Data;Wiek;Plec;Kod_Pocztowy;Zrodlo;Rejonowy_250;Rejonowy_750;Ogolno_1;Ogolno_2
    add_vote(votes2016, row[6], row[2])
    add_vote(votes2016, row[7], row[2])
    add_vote(votes2016, row[8], row[2])
    add_vote(votes2016, row[9], row[2])


def gen_year(votes, srcfile, outfile, pointfile=None):
  print('generating: ', outfile)
  with open(srcfile, 'r') as f:
    j = json.load(f)

    with open(outfile, 'w') as csvfile:

      if pointfile:
        with open(pointfile, 'w') as pf:
          print('generating: ', pointfile)
          for k in sorted(j.keys(), key=int):
            proj = j[k]
            w = csv.writer(pf, delimiter=',')
            for p in proj['points']:
              w.writerow([k, p['latitude'], p['longitude']])

      writer = csv.writer(csvfile, delimiter=',')
      writer.writerow(['id',
                       'status',
                       'votes',
                       'title',
                       'avg_age',
                       'polarity',
                       'budget',
                       'point/cost',
                       'points',
                       'category',
                       'level',
                       'district',
                       'detailed_localization',
                       'description',
                       'attachments'])

      for k in sorted(j.keys(), key=int):
        proj = j[k]

        status = 'bd'
        s = proj['status']
        if 'Nie wybrany' in s:
          status = 'niewybrany'
        elif 'wycofany' in s:
          status = 'wycofany'
        elif 'Wybrany' in s:
          status = 'wybrany'
        elif 'Projekt' in s:
          status = 'wycofany'

        text = Text(proj['title']+proj['description'])
        polarity = 0
        try:
          polarity = sum([w.polarity for w in text.words])
        except:
          print(text)

        avg_age = 0
        try:
          avg_age = numpy.mean(votes[k])
        except:
          pass

        pts = 1 if len(proj['points']) == 0 else len(proj['points'])
        pt_cost = int(proj['budget']) / pts

        row = [k,
               status,
               proj['votes'],
               proj['title'],
               avg_age,
               polarity,
               proj['budget'],
               pt_cost,
               pts,
               proj['category'],
               proj['level'],
               proj['district'],
               proj['detailed_localization'],
               proj['description'],
               proj['attachments']]

        writer.writerow(row)


gen_year({}, 'data/2016-12-03-projects-wbo2014.json', 'data/projects_2014.csv')
gen_year(votes2015, 'data/2016-12-03-projects-wbo2015.json', 'data/projects_2015.csv', 'data/points_2015.csv')
gen_year(votes2016, 'data/2016-12-03-projects-wbo2016.json', 'data/projects_2016.csv', 'data/points_2016.csv')

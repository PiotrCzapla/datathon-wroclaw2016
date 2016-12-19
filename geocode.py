#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-


from geopy.geocoders import GoogleV3
import csv
import sys
import argparse as ap
import time
import re

# https://developers.google.com/maps/documentation/geocoding/start#get-a-key
APIKEY=''
zipcode_file='data/keys.csv'

RE_ZIPCODE = re.compile(r'[0-9]{2,2}-[0-9]{3,3}')

geolocator = GoogleV3(api_key=APIKEY, timeout=10)

codes = {}


with open(zipcode_file, 'r') as kcsv:
  keyreader = csv.reader(kcsv)
  codes = {rows[0]:[rows[1], rows[2]] for rows in keyreader}


locfind_limit = 0


with open(zipcode_file, 'a+') as kcsv:
  keywriter = csv.writer(kcsv)

  def locfind(c):
    global locfind_limit
    try:
      return geolocator.geocode(c+', Polska')
    except:
      if 'geopy.exc.GeocoderQuotaExceeded' in str(sys.exc_info()[0]):
        print('API key request limit exceeded, try later.')
        sys.exit(0)
      print(e)
      if locfind_limit == 5:
        locfind_limit = 0
        return None
      else:
        locfind_limit += 1
      print('had to retry', c, 'sleeping 5')
      time.sleep(5)
      return locfind(c)

  def newvotes(legend, oldfile, newfile, zipindex):
    global RE_ZIPCODE

    with open(newfile, 'w') as csvvotesnew:
      writer = csv.writer(csvvotesnew)
      writer.writerow(legend)

      with open(oldfile, 'r') as csvvotes:
        reader = csv.reader(csvvotes, delimiter=';')
        for row in reader:
          code = row[zipindex]
          if code and not RE_ZIPCODE.match(code):
            print('Found bad zipcode:', code)
            print(row)
            csvvotesnew.close()
            csvvotes.close()
            sys.exit(1)
          latlon = [0, 0]
          try:
            latlon = codes[code]
            print('got cached', latlon)
          except:
            location = None
            location = locfind(code)

            if not location:
              d = {'latitude':0, 'longitude':0}
              location = ap.Namespace(**d)

            keywriter.writerow([code, location.latitude, location.longitude])

            codes[code] = [location.latitude, location.longitude]
            latlon = codes[code]
            print('got requested', latlon)

          writer.writerow(row + latlon)


  newvotes(['Lp', 'Data', 'Wiek', 'Plec', 'Osiedle', 'Kod_Pocztowy', 'Zrodlo', 'Prog_1','Prog_2', 'Prog_3', 'Lat', 'Lon'], 'data/votes_2015_encodingfix.csv', 'data/votes_2015_points.csv', 5)
  print('!!!!!! 2016')
  newvotes(['Lp', 'Data', 'Wiek', 'Plec', 'Kod_Pocztowy', 'Zrodlo', 'Rejonowy_250', 'Rejonowy_750','Ogolno_1', 'Ogolno_2', 'Lat', 'Lon'], 'data/2016-12-03-WBO_lista_glosow_2016.csv', 'data/votes_2016_points.csv', 4)
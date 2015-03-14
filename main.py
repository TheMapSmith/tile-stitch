import os
import urllib2
import json
import csv
import sys
from tiles import do_work
 
csv.register_dialect('excel', delimiter=':', quoting=csv.QUOTE_NONE)
zoom = 13  # What level zoom do you want to render the map? WARNING: High zooms result in giant files!
base_folder = '/Users/iandouglas/Dropbox/golf'
courses = {}
 
response = urllib2.urlopen(
    'https://raw.githubusercontent.com/TheMapSmith/GeoJSON-GolfCourses/master/north-american-golf-courses.geojson')
if response.code == 200:
    # try/except around read()
    data = response.read()
    payload = None
    if data:
        try:
            payload = json.loads(data)
        except ValueError as e:
            print e.message
 
    if 'features' in payload:
        properties = payload['features']
        if len(properties) > 0:
            rows = 0
            for one_property in properties:
                name = one_property['properties']['name']
                name = name.replace('/', ' ')
 
                if 'bbox' in one_property:
                    if name not in courses:
                        courses[name] = []
 
                    courses[name].append(one_property['bbox'])
 
    for property_name in courses:
        bbox_number = 0
        for bbox in courses[property_name]:
            property = courses[property_name]
            bbox_number += 1
            try:
                os.mkdir(base_folder + '/' + property_name)
            except OSError:
                pass
 
            try:
                os.mkdir(base_folder + '/' + property_name + '/%d' % (bbox_number))
            except OSError:
                pass
 
            filename = base_folder + '/' + property_name + '/%d' % (bbox_number) + '/%s-%d.csv' % (property_name, bbox_number)
 
            csv_output = open(filename, 'w')
            csv_writer = csv.writer(csv_output)
            lng1, lat1, lng2, lat2 = property[int(bbox_number)-1]
 
            csv_writer.writerow(['%0.16f' % lat1, '%0.16f' % lng1])
            csv_writer.writerow(['%0.16f' % lat2, '%0.16f' % lng2])
 
            csv_output.close()
 
            do_work(base_folder + '/' + property_name + '/%d' % (bbox_number), filename, zoom)
 
else:
    print response.code

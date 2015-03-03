import urllib2
import json
import csv

courses_GeoJSON = 'PATH TO GEOJSON' # pointed to a polygon outline GeoJSON file
csv.register_dialect('excel', delimiter=':', quoting=csv.QUOTE_NONE)


response = urllib2.urlopen(courses_GeoJSON)
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
            # try/except around open()
            csv_output = open('courses.csv', 'w')
            # try/except around csv_writer()
            csv_writer = csv.writer(csv_output)
            rows = 0
            for one_property in properties:
                if 'bbox' in one_property:
                    rows += 1
                    lng1, lat1, lng2, lat2 = one_property['bbox']
                    # try/except around writerow() calls
                    csv_writer.writerow(['%0.16f' % lat1, '%0.16f' % lng1])
                    csv_writer.writerow(['%0.16f' % lat2, '%0.16f' % lng2])

        print 'wrote %d rows' % rows
else:
    print response.code

# tile-stitch
Stitching tiles with Python

Original credit to [Ossum](https://www.facebook.com/ossumdesigns) from [Instructables](http://www.instructables.com/member/ossum/) for publishing [the code](http://www.instructables.com/id/Animated-Watercolour-Map-for-Cycle-TourRace-Video/#step0) which got me 99% of the way there. 

##tile-stitch.py

Reads extents from a single CSV file and downloads tiles within the extents and then stitches them together into a large file 

##geojson_to_extents_csv.py

Reads the 'bbox' property from a GeoJSON file and outputs the coordinate pairs to a massive CSV

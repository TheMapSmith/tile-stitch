import math
import os.path
import urllib
 
 
def trace_import_csv(fname):
    """ Function to Read in trace from csv """
    import csv
    trace = []
    for lat, lon in csv.reader(open(fname, 'r')):
        trace.append([float(lat), float(lon)])
 
    return trace
 
 
def trace_boundaries(trace):
    """ Function to get trace boundries """
    lat = zip(*trace)[0]
    lon = zip(*trace)[1]
 
    return {"north": max(lat), "south": min(lat), "east": max(lon), "west": min(lon)}
 
 
def deg2num(lat_deg, lon_deg, zoom):
    """ Function to convert lat,lon degrees to tile x/y number """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x_tile = int((lon_deg + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return x_tile, y_tile
 
 
def num2deg(xtile, ytile, zoom):
    """ Function to convert xy tile to NW corner of tile """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg
 
 
def determine_tile_range(boundaries, zoom):
    """ Determine tile range given boundaries and zoom """
    x_max, y_min = deg2num(boundaries["north"], boundaries["east"], zoom)
    x_min, y_max = deg2num(boundaries["south"], boundaries["west"], zoom)
    return {"xMin": x_min, "xMax": x_max, "yMin": y_min, "yMax": y_max}
 
 
def get_tiles(path, xy_range, zoom, style_string=None):
    """ Take a tile range and download them (if not locally present) """
    # set acive directory to that of the script
    currentdir = os.curdir
    tile_dir = os.path.join(currentdir, path)  # Here put the path to a place to store the tiles
 
    tile_server_url = "http://c.tile.openstreetmap.org/"  # Here put the URL to the tile server
 
    # create a list of all the x and y coordinates to download
    x_range = range(xy_range["xMin"], xy_range["xMax"]+1)
    y_range = range(xy_range["yMin"], xy_range["yMax"]+1)
 
    for x in x_range:
        for y in y_range:
            # define the file name
            tile_filename = str(y)+".png"
 
            # define the local path as well as the complete path to the local and remote files
            local_path = os.path.join(tile_dir, str(zoom), str(x))
            local_file = os.path.join(local_path, tile_filename)
            url = tile_server_url+str(zoom)+"/"+str(x)+"/"+str(y)+".png"
            # but @2x.png or @3x or @4x for different size tiles
            if style_string:
                url += style_string  # Sometimes tile paths need a style string (like MapBox Studio tiles)
 
            # check if the file exists locally
            if not os.path.isfile(local_file):
                print "retrieving " + url
                # if local directory doesn't yet exist, make it
                if not os.path.isdir(local_path):
                    os.makedirs(local_path)
                # retrieve the file from the server and save it
                urllib.urlretrieve(url, local_file)
 
 
def merge_tiles(path, xy_range, zoom, filename):
    """ Merge tiles into one image """
    from PIL import Image
    tile_size = 256  # For 1x tiles: 256 2x: 512 3x: 768 4x: 1024
    tile_dir = os.path.join(os.getcwd(), path, str(zoom))  # Put the same local directory as above for the tiles
 
    out = Image.new('RGBA',
                    ((xy_range["xMax"]-xy_range["xMin"]+1) * tile_size,
                     (xy_range["yMax"]-xy_range["yMin"]+1) * tile_size))
 
    imx = 0
    for x in range(xy_range["xMin"], xy_range["xMax"]+1):
        imy = 0
        for y in range(xy_range["yMin"], xy_range["yMax"]+1):
            tile_file = os.path.join(tile_dir, str(x), str(y)+".png")
            tile = Image.open(tile_file)
            out.paste(tile, (imx, imy))
            imy += tile_size
        imx += tile_size
 
    out.save(os.path.join(os.curdir, filename))
 
 
def do_work(path, filename, zoom):
    # define parameters
    trace = trace_import_csv(filename)  # This file contains the two corner boundaries of the map to be rendered
 
    # determine the boundaries of the trace
    boundaries_trace = trace_boundaries(trace)
 
    # determine xy numbers of boundary tiles
    tile_range = determine_tile_range(boundaries_trace, zoom)
 
    # count number of tiles in x and y direction
    x_tiles = tile_range["xMax"]-tile_range["xMin"]
    y_tiles = tile_range["yMax"]-tile_range["yMin"]
    num_tiles = x_tiles*y_tiles
 
    print "fetching " + str(num_tiles) + " tiles"
    # download tiles if needed
    get_tiles(path, tile_range, zoom)
    print "Got all the tiles. Merging"
 
    # merge tiles into oneimage
    merge_tiles(path, tile_range, zoom, filename.replace('.csv', '.png'))  # Output file path and type
 
    # print final stats
    print "boundaries: ", boundaries_trace
    print "tile X,Y range: ", tile_range
    print "x tiles: ", x_tiles
    print "y tiles: ", y_tiles
    print "num tiles: ", num_tiles

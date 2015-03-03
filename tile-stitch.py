import csv
import math
import os.path
import urllib

### Function to Read in trace from csv ###
def traceImportCSV(fname):
    import csv
    trace = []
    for lat,lon in csv.reader(open(fname,'r')):
        trace.append([float(lat),float(lon)])

    return trace

### Function to get trace boundries ###_
def traceBoundaries(trace):

    lat = zip(*trace)[0]
    lon = zip(*trace)[1]

    return {"north":max(lat),"south":min(lat),"east":max(lon),"west":min(lon)}


### Function to convert lat,lon degrees to tile x/y number ### 
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)

### Function to convert xy tile to NW corner of tile ###
def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

### Determine tile range given boundaries and zoom ###
def determineTileRange(boundaries,zoom):
    Xmax,Ymin = deg2num(boundaries["north"],boundaries["east"],zoom)
    Xmin,Ymax = deg2num(boundaries["south"],boundaries["west"],zoom)
    return {"xMin":Xmin,"xMax":Xmax,"yMin":Ymin,"yMax":Ymax}

### Take a tile range and download them (if not locally present) ###
def getTiles(xyRange,zoom):
    #set acive directory to that of the script
    currentdir = os.curdir
    tileDir = os.path.join(currentdir,"LOCAL DIR") # Here put the path to a place to store the tiles 

    tileServerUrl = "WEB PATH" # Here put the URL to the tile server 

    #create a list of all the x and y coordinates to download
    xRange = range(xyRange["xMin"],xyRange["xMax"]+1)
    yRange = range(xyRange["yMin"],xyRange["yMax"]+1)

    for x in xRange:
        for y in yRange:
            #define the file name
            tileFileName = str(y)+".png"

            #define the local path as well as the complete path to the local and remote files
            localPath = os.path.join(tileDir,str(zoom),str(x))
            localFile = os.path.join(localPath,tileFileName)
            preFile = tileServerUrl+str(zoom)+"/"+str(x)+"/"+str(y)+".png" # This part stiches together the  WEB PATH with the standard X/Y/Z.png ending
            # remoteFile = preFile + "STYLE STRING" ## Sometimes tile paths need a style string (like MapBox Studio tiles)

            #check if the file exists locally
            if not os.path.isfile(localFile):                 
                print "retrieving "+remoteFile
                #if local directory doesn't yet exist, make it
                if not os.path.isdir(localPath):
                    os.makedirs(localPath)
                #retrieve the file from the server and save it    
                urllib.urlretrieve(remoteFile,localFile)

### Merge tiles into one image ###
def mergeTiles(xyRange,zoom,filename):
    from PIL import Image
    tileSize = 256
    tileDir = os.path.join(os.getcwd(),"LOCAL DIR",str(zoom)) # Put the same local directory as above for the tiles

    out = Image.new( 'RGBA', ((xyRange["xMax"]-xyRange["xMin"]+1) * tileSize, (xyRange["yMax"]-xyRange["yMin"]+1) * tileSize) ) 

    imx = 0;
    for x in range(xyRange["xMin"], xyRange["xMax"]+1):
        imy = 0
        for y in range(xyRange["yMin"], xyRange["yMax"]+1):
            tileFile = os.path.join(tileDir,str(x),str(y)+".png")
            tile = Image.open(tileFile)
            out.paste( tile, (imx, imy) )
            imy += tileSize
        imx += tileSize

    out.save(os.path.join(os.curdir,filename))



# define parameters
zoom = 18 # What level zoom do you want to render the map? WARNING: High zooms result in giant files!
trace = traceImportCSV("PATH TO CSV FILE") # This file contains the two corner boundaries of the map to be rendered

# determine the boundaries of the trace
boundaries_trace = traceBoundaries(trace)

# determine xy numbers of boundary tiles
tileRange = determineTileRange(boundaries_trace,zoom)

# count number of tiles in x and y direction
xTiles = tileRange["xMax"]-tileRange["xMin"]
yTiles = tileRange["yMax"]-tileRange["yMin"]
numTiles = xTiles*yTiles

print "fetching " + str(numTiles) + " tiles"
# download tiles if needed
getTiles(tileRange,zoom)
print "Got all the tiles. Merging"

# merge tiles into oneimage
mergeTiles(tileRange,zoom,"OUTPUT FILE") # Output file path and type 


# print final stats
print "boundaries: ",boundaries_trace
print "tile X,Y range: ",tileRange
print "x tiles: ",xTiles
print "y tiles: ",yTiles
print "num tiles: ",numTiles

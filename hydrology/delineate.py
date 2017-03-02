import os, tempfile, json
from osgeo import gdal, ogr
import numpy as np
from gdalconst import GDT_Int32
import kml2geojson

contributions = {
    (0, 0): 2,
    (0, 1): 4,
    (0, 2): 8,
    (1, 0): 1,
    (1, 1): 0,
    (1, 2): 16,
    (2, 0): 128,
    (2, 1): 64,
    (2, 2): 32
}


def lonlat2xy(lon, lat, gt):
    """Convert the map coordinates (lon, lat) to grid coordinates (x, y)"""
    x = int((lon - gt[0]) / gt[1])  # x pixel
    y = int((lat - gt[3]) / gt[5])  # y pixel
    return x, y


def xy2lonlat(x, y, gt):
    """Convert grid coordinates (x, y) to map coordinates (lon, lat)"""
    lon = x * gt[1] + gt[0]
    lat = y * gt[5] + gt[3]
    return lon, lat


def findregion(lat, lon):
    # find raster
    if 6 < lat < 38 and -118 < lon < -61:
        region = 'ca'
    elif -56 < lat < 15 and -93 < lon < -32:
        region = 'sa'
    elif 24 < lat < 61 and -138 < lon < -52:
        region = 'na'
    elif 12 < lat < 62 and -14 < lon < 70:
        region = 'eu'
    elif -35 < lat < 38 and -19 < lon < 55:
        region = 'af'
    elif -12 < lat < 61 and 57 < lon < 180:
        region = 'as'
    elif -56 < lat < -10 and 112 < lon < 180:
        region = 'au'
    else:
        region = None

    return region


def delineate(coords, basepath, cellsize):
    # register the bil driver
    bildriver = gdal.GetDriverByName('EHdr')
    bildriver.Register()

    geodriver = gdal.GetDriverByName('GTiff')
    geodriver.Register()

    src = {}

    catchments = {}

    # initialize pour points
    for i, (lat, lon) in enumerate(coords):

        region = findregion(lat, lon)

        if i==0:
            originRegion = region

        if region not in src:
            dataset = '{}_dir_{}s'.format(region, cellsize)

            # identify raster path
            bilpath = os.path.join(basepath, "%s_bil" % dataset, "%s.bil" % dataset)

            # create the gdal flow direction grid from the bil
            bil = gdal.Open(bilpath)

            src[region] = {}
            src[region]['gt'] = bil.GetGeoTransform()
            src[region]['fdir'] = bil.GetRasterBand(1)

        x, y = lonlat2xy(lon, lat, src[originRegion]['gt'])
        val = i + 1
        catchments[(x, y)] = val

    for i, (lat, lon) in enumerate(coords):

        # the core routine to find the catchment
        def update_catchments(region, x, y, xt, yt, val):
            fdir = src[region]['fdir']
            area = fdir.ReadAsArray(x - 1, y - 1, 3, 3)  # does not account for edge cases yet

            catchments[(xt, yt)] = val

            for i in range(3):  # rows
                for j in range(3):  # columns
                    if area[i, j] == contributions[(i, j)]:
                        xnew = x + (j - 1)
                        ynew = y + (i - 1)
                        xtnew = xt + (j - 1)
                        ytnew = yt + (i - 1)

                        # need to update region here based on xnew, ynew
                        # in the meantime, just assume the region is the same
                        if (xtnew, ytnew) not in catchments:
                            update_catchments(region, xnew, ynew, xtnew, ytnew, val)

        # load initial region of point
        x, y = lonlat2xy(lon, lat, src[region]['gt'])
        xt, yt = lonlat2xy(lon, lat, src[originRegion]['gt'])
        val = i + 1

        # update catchments
        update_catchments(region, x, y, xt, yt, val)

    # create numpy array
    xmin = min([x for (x, y) in catchments])
    xmax = max([x for (x, y) in catchments])
    ymin = min([y for (x, y) in catchments])
    ymax = max([y for (x, y) in catchments])

    # get the cols & rows
    cols = xmax - xmin + 1
    rows = ymax - ymin + 1
    array = np.zeros((rows, cols))

    for (x, y), val in catchments.items():
        xnorm = x - xmin
        ynorm = y - ymin
        array[ynorm, xnorm] = val

    # define raster origin
    originLon, originLat = xy2lonlat(xmin, ymin, src[originRegion]['gt'])
    cellWidth = cellHeight = cellsize / 60 / 60

    layername = 'catchments'
    with tempfile.TemporaryDirectory() as tmpdir:
        # create catchments raster
        tmppath = os.path.join(tmpdir, 'out.tif')
        geotiff = geodriver.Create(tmppath, cols, rows, 1, GDT_Int32)
        geotiff.SetGeoTransform((originLon, cellWidth, 0, originLat, 0, -cellHeight))
        geoband = geotiff.GetRasterBand(1)
        geoband.WriteArray(array)

        # prepare output vector (kml) layer
        # NB: GDAL's GeoJSON output is not formatted correctly. So the hack here
        # is to output to kml, then convert to geojson using the kml2geojson module.
        driver = ogr.GetDriverByName('KML')
        tmpkmlpath = os.path.join(tmpdir, layername + '.kml')
        tmpkmlsrc = driver.CreateDataSource(tmpkmlpath)
        tmplayer = tmpkmlsrc.CreateLayer(layername, srs=None)

        # add field
        subwatid = ogr.FieldDefn('id', ogr.OFTInteger)
        tmplayer.CreateField(subwatid)

        # The "2" here indicates to write the GeoTIFF values to the "id" column.
        # Other options are 1: "name" column and 2: "description" column
        gdal.Polygonize(geoband, None, tmplayer, 2, [], callback=None)

        # geotiff.FlushCache()
        del geoband
        del geotiff
        del tmpkmlsrc
        del tmplayer

        kml2geojson.main.convert(tmpkmlpath, tmpdir)
        with open(tmpkmlpath.replace('.kml', '.geojson')) as f:
            gj = json.loads(f.read())
            gj['features'] = [f for f in gj['features'] if f['properties']['id'] != '0']

    return gj

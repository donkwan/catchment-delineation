#!flask/bin/python
from flask import Flask, request, jsonify
from hydrology import delineate


application = Flask(__name__)
#application.config['BASEPATH'] = '/efs/hydrodata'
application.config['BASEPATH'] = r'D:\Users\david\Documents\GitHub\catchment-delineation\hydrodata'

@application.route('/')
def index():
    return 'Hello, hydrologist!'


@application.route('/api/delineate_point')
def delineate_point_api():
    """
    Delineate a single point.
    """
    lat = request.args.get('lat', None, type=float)
    lon = request.args.get('lon', None, type=float)
    cellsize = request.args.get('cellsize', 15, type=float)
    featuretype = request.args.get('type', 'Feature', type=str)

    if lat is None or lon is None:
        return 'Hello, again! Did you forget a lat or lon?'

    else:
        gj = delineate.delineate([(lat, lon)], application.config['BASEPATH'], cellsize, featuretype)
        return jsonify(geojson=gj)


@application.route('/api/delineate_points', methods=['GET', 'POST'])
def delineate_points_api():
    if request.method=='GET':
        coords = eval(request.args.get('coords', 'None'))
        cellsize = request.args.get('cellsize', 15, type=float)
    else:
        coords = request.json['coords']
        cellsize = request.json['cellsize'] if 'cellsize' in request.json else 15

    if coords is None:
        return 'Hello, again! Did you forget the coords? [(lat1,lon1),(lat2,lon2),...]'

    else:
        basepath = application.config['BASEPATH']
        gj = delineate.delineate(coords, basepath, cellsize)
        return jsonify(geojson=gj)


if __name__ == '__main__':
    #application.run(host='0.0.0.0', port=8080, debug=True)
    application.run(port=5001, debug=False)

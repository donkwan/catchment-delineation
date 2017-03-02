#!flask/bin/python
from flask import Flask, request
from hydrology import delineate


application = Flask(__name__)
application.config['BASEPATH'] = '/efs/hydrodata'


@application.route('/')
def index():
    return 'Hello, hydrologist!'


@application.route('/api/delineate_point')
def delineate_point_api():
    lat = request.args.get('lat', None, type=float)
    lon = request.args.get('lon', None, type=float)
    cellsize = request.args.get('cellsize', 15, type=float)

    if lat is None or lon is None:
        return 'Hello, again! Did you forget a lat or lon?'

    else:
        gj = delineate.delineate([(lat, lon)], application.config['BASEPATH'], cellsize)
        return gj


@application.route('/api/delineate_points')
def delineate_points_api():
    coords = eval(request.args.get('coords', 'None'))
    cellsize = request.args.get('cellsize', 15, type=float)

    if coords is None:
        return 'Hello, again! Did you forget the coords? [(lat1,lon1),(lat2,lon2),...]'

    else:
        basepath = application.config['BASEPATH']
        gj = delineate.delineate(coords, basepath, cellsize)
        return gj


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, debug=True)
    # application.run(port=8080, debug=True)

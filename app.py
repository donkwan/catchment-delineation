#!flask/bin/python
from flask import Flask, request
from hydrology import delineate

app = Flask(__name__)


app.config.from_pyfile('./settings.cfg')
app.config.from_pyfile('./instance/application.cfg', silent=True)


@app.route('/')
def index():
    return 'Hello, hydrologist!'


@app.route('/api/delineate_point')
def delineate_point_api():
    lat = request.args.get('lat', None, type=float)
    lon = request.args.get('lon', None, type=float)
    cellsize = request.args.get('cellsize', 15, type=float)

    if lat is None or lon is None:
        return 'Hello, again!'

    else:
        gj = delineate.delineate([(lat, lon)], app.config['BASEPATH'], cellsize)
        return gj


@app.route('/api/delineate_points')
def delineate_points_api():
    coords = eval(request.args.get('coords', 'None'))
    cellsize = request.args.get('cellsize', 15, type=float)

    if coords is None:
        return 'Hello, again!'

    else:
        basepath = app.config['BASEPATH']
        gj = delineate.delineate(coords, basepath, cellsize)
        return gj


if __name__ == '__main__':
    app.run(debug=False, port=80)

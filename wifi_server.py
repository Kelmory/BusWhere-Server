import os
import sys
import json

from flask import Flask, escape, request
from sqlalchemy import create_engine

sys.path.append(os.getcwd())


SQL_DB_NAME = 'nsw_bus2.db'
ENGINE = 'sqlite:///' + os.getcwd() + '\\' + SQL_DB_NAME

API_KEY = 'api-key'

app = Flask(__name__)


#
#   Utils for authentication
#
def api_key_check(api_key: str) -> bool:
    return True

#
#   Flask routing logic
#
@app.route('/')
def hello():
    name = request.args.get('name', 'World')
    return f'Hello, {escape(name)}!'


@app.route('/location/save', methods=['POST'])
def save():
    api_key = request.args.get(API_KEY)
    if api_key_check(api_key):

        return
    else:
        return {'message': 'invalid api key'}, 401


@app.route('/location/get', methods=['GET'])
def get():
    api_key = request.args.get(API_KEY)
    if api_key_check(api_key):

        return
    else:
        return {'message': 'invalid api key'}, 401


@app.route('/buses/get', methods=['GET'])
def get_bus_stop():
    api_key = request.args.get(API_KEY)
    if api_key_check(api_key):
        conn = create_engine(ENGINE)
        request_type = request.args.get('request_type', type=str)
        sql = parse_request(request, request_type)
        if sql is not None:
            with conn.connect() as connection:
                try:
                    result = connection.execute(sql)
                except Exception as e:
                    print(e)
                    return 'invalid parameters', 404
                else:
                    data = []
                    for row in result:
                        data.append(row._row)
                    return json.dumps(data)
        else:
            return 'invalid parameters', 404


# SQL injection
def inject_stops(m_request):
    lat1 = m_request.args.get('lat1')
    lat2 = m_request.args.get('lat2')
    lng1 = m_request.args.get('lng1')
    lng2 = m_request.args.get('lng2')
    sql = "SELECT DISTINCT stop_id, stop_name, stop_lat, stop_lon\n " \
          "FROM stops\n " \
          "WHERE stop_lat > %s AND stop_lat < %s AND stop_lon > %s AND stop_lon < %s"
    sql = sql % (lat1, lat2, lng1, lng2)
    return sql


def inject_buses(m_request):
    stop_id = m_request.args.get('stop_id')
    sql = "select DISTINCT routes.route_id," \
          "routes.route_short_name, routes.route_long_name\n " \
          "from stop_times INDEXED by quick_stop_times\n " \
          "left join stops On stop_times.stop_id = stops.stop_id\n " \
          "left join trips on stop_times.trip_id = trips.trip_id\n " \
          "LEFT join routes on trips.route_id = routes.route_id\n " \
          "where stops.stop_id = %s\n" \
          "order by routes.route_short_name"
    sql = sql % (stop_id)
    return sql


def inject_stop_from_name(m_request):
    name = m_request.args.get('name')
    sql = "SELECT stop_id, stop_name, stop_lat, stop_lon " \
          "FROM stops " \
          "WHERE stop_name LIKE '%s'"
    sql = sql % name
    return sql


def inject_bus_from_stop(m_request):
    name = m_request.args.get('name')
    sql = "select DISTINCT routes.route_id, routes.route_short_name, routes.route_long_name \n" \
          "from stop_times INDEXED by quick_stop_times \n" \
          "left join stops On stop_times.stop_id = stops.stop_id\n" \
          "left join trips on stop_times.trip_id = trips.trip_id\n" \
          "LEFT join routes on trips.route_id = routes.route_id\n" \
          "where stops.stop_name is %s "
    sql = sql % name
    return sql


def inject_latlng_from_route(m_request):
    route_id = m_request.args.get('route_id')
    direction_id = m_request.args.get('direction_id')
    sql = "select DISTINCT shape_pt_lat, shape_pt_lon, shape_pt_sequence\n" \
          "from routes\n" \
          "LEFT JOIN trips on routes.route_id = trips.route_id\n" \
          "LEFT JOIN shapes on shapes.shape_id = trips.shape_id\n" \
          "where routes.route_id = %s and trips.direction_id = %s\n" \
          "ORDER by shapes.shape_id, shape_pt_sequence"
    sql = sql % (route_id, direction_id)
    return sql


def inject_stops_from_route(m_request):
    route = m_request.args.get('route')
    sql = "select DISTINCT stop_id, stop_name, stop_lat, stop_lon\n" \
          "FROM stops\n" \
          "where stop_id in\n" \
          "(SELECT stop_id from stop_times\n" \
          "where trip_id =(\n" \
          "select trip_id from trips\n" \
          "where trip_id like '-%s-'\n" \
          "limit 1) \n" \
          "ORDER by stop_sequence)\n"
    sql = sql % route
    return sql


def parse_request(m_request: request, request_type: str) -> str:
    if request_type == 'get_stops':
        return inject_stops(m_request)
    elif request_type == 'get_buses':
        return inject_buses(m_request)
    elif request_type == 'get_buses_from_stop':
        return inject_bus_from_stop(m_request)
    elif request_type == 'get_stop_from_name':
        return inject_stop_from_name(m_request)
    elif request_type == 'get_latlng_from_route':
        return inject_latlng_from_route(m_request)
    elif request_type == 'get_stops_from_route':
        return inject_stops_from_route(m_request)
    return None


if __name__ is '__main__':
    app.run()

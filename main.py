import json,pymysql,time
from flask import Flask
from flask import request,redirect
import datetime
import decimal
import yaml


app = Flask(__name__)

db_config = None
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)
    db_config = config['mysql']


username = 'chitowdr'
auth_table = f'{username}_auth'
log_table = f'{username}_api_logs'
data_table = 'class_datapoints'

def auth(token):
    if token is None:
        return False
    conn = pymysql.connect(**db_config) 
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = f'SELECT * FROM `{auth_table}` WHERE `token` = %s;'
    cur.execute(sql,(token,))
    results = cur.fetchall()
    conn.close()
    if len(results) == 1:
        return True
    else:
        return False

def log(token,endpoint,response):
    conn = pymysql.connect(**db_config) 
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = f'INSERT INTO `{log_table}` (`endpoint`,`token`,`response`,`dt`) VALUES (%s,%s,%s,%s)'
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(sql,(endpoint,token,response,dt))
    conn.close()

def valid_date(d):
    try:
        datetime.datetime.strptime(d,'%Y-%m-%d %H:%M:%S')
        return True
    except Exception as e:
        return False

def clean_row(row):
    item = {}
    for k in row:
        v = row[k]
        if k == 'geo_point' or isinstance(v,bytes):
            continue 
        if isinstance(v,(datetime.datetime,datetime.date)):
            v = str(v)
        if isinstance(v,decimal.Decimal):
            v = float(v)
        item[k] = v
    return item

def fail(res,msg,response):
    res['code'] = 0
    res['msg'] = msg
    log(request.args.get('key'),res['req'],response)
    return json.dumps(res,indent=4)


@app.route("/", methods=['GET','POST'])
def root():
    res = {}
    res['code'] = 0
    res['msg'] = 'No endpoint specified'
    res['req'] = '/'
    res['sqltime'] = 0
    return json.dumps(res,indent=4)

@app.route("/getData", methods=['GET'])
def getData():
    res = {}
    res['req'] = 'getData'
    res['sqltime'] = 0
    if not auth(request.args.get('key')):
        return fail(res,'auth error','401')

    start = request.args.get('start')
    end = request.args.get('end')
    if start is None or end is None:
        return fail(res,'start and end need to be provided.','400')
    if not valid_date(start) or not valid_date(end):
        return fail(res,'start and end must look like YYYY-MM-DD HH:MM:SS','400')

    conn = pymysql.connect(**db_config) 
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = f'SELECT * FROM `{data_table}` WHERE `date_time` BETWEEN %s AND %s ORDER BY `date_time` LIMIT 0,500;'
    print(sql,start,end)
    t = time.time()
    cur.execute(sql,(start,end))
    rows = cur.fetchall()
    res['sqltime'] = time.time() - t
    conn.close()

    items = []
    for row in rows:
        items.append(clean_row(row))

    res['code'] = 1
    res['msg'] = 'ok'
    res['results'] = items
    res['num_results'] = len(items)
    log(request.args.get('key'),res['req'],'200')
    return json.dumps(res,indent=4)

@app.route("/countInPolygon", methods=['GET'])
def countInPolygon():
    res = {}
    res['req'] = 'countInPolygon'
    res['sqltime'] = 0
    if not auth(request.args.get('key')):
        return fail(res,'auth error','401')

    polygon = request.args.get('polygon')
    if polygon is None:
        return fail(res,'polygon needs to be provided.','400')


    points = []
    try:
        for p in polygon.split(','):
            xy = p.strip().split(' ')
            if len(xy) != 2:
                raise ValueError('bad point')
            points.append([float(xy[0]),float(xy[1])])
    except Exception as e:
        print(str(e))
        return fail(res,'polygon must be a list of numeric x y points like -74 42,-75 39,-74 41,-74 42','400')
    if len(points) < 4 or points[0] != points[-1]:
        return fail(res,'polygon needs at least 4 points and the last point must equal the first.','400')

    
    pts = []
    for p in points:
        pts.append(f'{p[0]} {p[1]}')
    wkt = 'Polygon((' + ','.join(pts) + '))'

    conn = pymysql.connect(**db_config) 
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = f'SELECT COUNT(*) AS `count` FROM `{data_table}` WHERE st_within(geo_point, ST_GeomFromText(%s,0));'
    print(sql,wkt)
    t = time.time()
    try:
        cur.execute(sql,(wkt,))
        row = cur.fetchone()
    except Exception as e:
        print(str(e))
        conn.close()
        return fail(res,'MySQL could not use that polygon.','400')
    res['sqltime'] = time.time() - t
    conn.close()

    res['code'] = 1
    res['msg'] = 'ok'
    res['polygon'] = wkt
    res['count'] = row['count']
    log(request.args.get('key'),res['req'],'200')
    return json.dumps(res,indent=4)

@app.route("/getAvgSpeedByFlight", methods=['GET'])
def getAvgSpeedByFlight():
    res = {}
    res['req'] = 'getAvgSpeedByFlight'
    res['sqltime'] = 0
    if not auth(request.args.get('key')):
        return fail(res,'auth error','401')

    start = request.args.get('start')
    end = request.args.get('end')
    where = []
    params = []
    if start is not None:
        if not valid_date(start):
            return fail(res,'start must look like YYYY-MM-DD HH:MM:SS','400')
        where.append('`date_time` >= %s')
        params.append(start)
    if end is not None:
        if not valid_date(end):
            return fail(res,'end must look like YYYY-MM-DD HH:MM:SS','400')
        where.append('`date_time` <= %s')
        params.append(end)

    sql = f'SELECT AVG(gs) AS `avg_gs`,`flight_num` FROM `{data_table}`'
    if len(where) > 0:
        sql += ' WHERE ' + ' AND '.join(where)
    sql += ' GROUP BY `flight_num` ORDER BY `flight_num` LIMIT 0,500;'

    conn = pymysql.connect(**db_config) 
    cur = conn.cursor(pymysql.cursors.DictCursor)
    print(sql,params)
    t = time.time()
    cur.execute(sql,params)
    rows = cur.fetchall()
    res['sqltime'] = time.time() - t
    conn.close()

    items = []
    for row in rows:
        item = {}
        item['flight_num'] = row['flight_num']
        item['avg_gs'] = None
        if row['avg_gs'] is not None:
            item['avg_gs'] = float(row['avg_gs'])
        items.append(item)

    res['code'] = 1
    res['msg'] = 'ok'
    res['results'] = items
    res['num_results'] = len(items)
    log(request.args.get('key'),res['req'],'200')
    return json.dumps(res,indent=4)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)

import requests, json

base = 'http://127.0.0.1:5000'

def call(label,url):
    print('-----',label)
    print(url)
    r = requests.get(url)
    resp = json.loads(r.text)
    print('code:',resp['code'],'| msg:',resp['msg'],'| req:',resp['req'],'| sqltime:',resp['sqltime'])
    return resp


# ---------- getData ----------
resp = call('getData - good request', base + '/getData?key=123&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15')
print(resp['num_results'], 'records')
if resp['num_results'] > 0:
    print('first record:', resp['results'][0])

call('getData - wrong key (should fail)', base + '/getData?key=1234&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15')
call('getData - no key (should fail)', base + '/getData?start=2022-11-23 05:28:10&end=2022-11-23 05:28:15')
call('getData - missing end (should fail)', base + '/getData?key=123&start=2022-11-23 05:28:10')
call('getData - bad date (should fail)', base + '/getData?key=123&start=yesterday&end=2022-11-23 05:28:15')


# ---------- countInPolygon ----------
resp = call('countInPolygon - good request', base + '/countInPolygon?key=123&polygon=-74 42,-75 39,-74 41,-74 42')
print(resp['count'], 'points in polygon')

call('countInPolygon - wrong key (should fail)', base + '/countInPolygon?key=1234&polygon=-74 42,-75 39,-74 41,-74 42')
call('countInPolygon - missing polygon (should fail)', base + '/countInPolygon?key=123')
call('countInPolygon - not closed (should fail)', base + '/countInPolygon?key=123&polygon=-74 42,-75 39,-74 41')
call('countInPolygon - not numbers (should fail)', base + '/countInPolygon?key=123&polygon=a b,c d,e f,a b')


# ---------- getAvgSpeedByFlight ----------
resp = call('getAvgSpeedByFlight - with dates', base + '/getAvgSpeedByFlight?key=123&start=2022-11-23 05:00:00&end=2022-11-23 08:00:00')
print(resp['num_results'], 'flights')
for item in resp['results'][0:5]:
    print(item['flight_num'], item['avg_gs'])

resp = call('getAvgSpeedByFlight - no dates (optional)', base + '/getAvgSpeedByFlight?key=123')
print(resp['num_results'], 'flights')

call('getAvgSpeedByFlight - wrong key (should fail)', base + '/getAvgSpeedByFlight?key=1234')
call('getAvgSpeedByFlight - bad date (should fail)', base + '/getAvgSpeedByFlight?key=123&start=nope')

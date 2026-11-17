# ADSB API

Flask API over the `class_datapoints` ADSB table in MySQL.

## Files

- `main.py`
- `test-client.py`
- `setup-tables.py`

## Setup

```sql
CREATE TABLE `chitowdr_auth` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `token` VARCHAR(64) NOT NULL
);
INSERT INTO `chitowdr_auth` (`token`) VALUES ('123');

CREATE TABLE `chitowdr_api_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `endpoint` VARCHAR(64),
    `token` VARCHAR(64),
    `response` VARCHAR(8),
    `dt` DATETIME
);
```

```
python main.py
python test-client.py
```

## Requests

Base URL: `http://127.0.0.1:5000`

```
/getData?key=123&start=2022-11-23 05:28:10&end=2022-11-23 05:28:15
/countInPolygon?key=123&polygon=-74 42,-75 39,-74 41,-74 42
/getAvgSpeedByFlight?key=123&start=2022-11-23 05:00:00&end=2022-11-23 08:00:00
```

## Response schemas

### getData

```json
{
    "type": "object",
    "required": ["code", "msg", "req", "sqltime"],
    "properties": {
        "code": {"type": "integer", "enum": [0, 1]},
        "msg": {"type": "string"},
        "req": {"type": "string", "const": "getData"},
        "sqltime": {"type": "number"},
        "num_results": {"type": "integer", "maximum": 500},
        "results": {
            "type": "array",
            "maxItems": 500,
            "items": {
                "type": "object",
                "properties": {
                    "dpid": {"type": "integer"},
                    "date_time": {"type": "string"},
                    "hex": {"type": ["string", "null"]},
                    "flight_num": {"type": ["string", "null"]},
                    "squawk": {"type": ["integer", "null"]},
                    "lat": {"type": ["number", "null"]},
                    "lon": {"type": ["number", "null"]},
                    "fid": {"type": ["integer", "null"]},
                    "gs": {"type": ["number", "null"]},
                    "alt_gps": {"type": ["integer", "null"]},
                    "alt_baro": {"type": ["integer", "null"]},
                    "cat": {"type": ["string", "null"]},
                    "track": {"type": ["number", "null"]},
                    "nav_heading": {"type": ["number", "null"]}
                }
            }
        }
    }
}
```

### countInPolygon

```json
{
    "type": "object",
    "required": ["code", "msg", "req", "sqltime"],
    "properties": {
        "code": {"type": "integer", "enum": [0, 1]},
        "msg": {"type": "string"},
        "req": {"type": "string", "const": "countInPolygon"},
        "sqltime": {"type": "number"},
        "polygon": {"type": "string"},
        "count": {"type": "integer", "minimum": 0}
    }
}
```

### getAvgSpeedByFlight

```json
{
    "type": "object",
    "required": ["code", "msg", "req", "sqltime"],
    "properties": {
        "code": {"type": "integer", "enum": [0, 1]},
        "msg": {"type": "string"},
        "req": {"type": "string", "const": "getAvgSpeedByFlight"},
        "sqltime": {"type": "number"},
        "num_results": {"type": "integer", "maximum": 500},
        "results": {
            "type": "array",
            "maxItems": 500,
            "items": {
                "type": "object",
                "required": ["flight_num", "avg_gs"],
                "properties": {
                    "flight_num": {"type": ["string", "null"]},
                    "avg_gs": {"type": ["number", "null"]}
                }
            }
        }
    }
}
```

import pymysql
import yaml



db_config = None
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)
    db_config = config['mysql']

username = 'chitowdr'

conn = pymysql.connect(**db_config) 
cur = conn.cursor(pymysql.cursors.DictCursor)

sql = f'''CREATE TABLE IF NOT EXISTS `{username}_auth` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `token` VARCHAR(64) NOT NULL
);'''
cur.execute(sql)
print(f'{username}_auth table ready')

cur.execute(f'SELECT * FROM `{username}_auth` WHERE `token` = %s;',('123'))
if len(cur.fetchall()) == 0:
    cur.execute(f'INSERT INTO `{username}_auth` (`token`) VALUES (%s);',('123'))
    print('key 123 added')
else:
    print('key 123 already there')


sql = f'''CREATE TABLE IF NOT EXISTS `{username}_api_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `endpoint` VARCHAR(64),
    `token` VARCHAR(64),
    `response` VARCHAR(8),
    `dt` DATETIME
);'''
cur.execute(sql)
print(f'{username}_api_logs table ready')

conn.close()
print('done')

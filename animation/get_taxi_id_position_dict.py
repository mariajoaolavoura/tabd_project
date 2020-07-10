import psycopg2
from postgis.psycopg import register

## Get the match between taxi's id in the db with that taxi's column in offsets.
## Create a dict { key=taxi_id_db, value=offsets_columns}
conn = psycopg2.connect("dbname=TABD user=postgres password=' ' ")
register(conn)
cursor_psql = conn.cursor()

sql = """select distinct taxi from tracks order by 1"""
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

taxi_id_position = {}
for pos, taxi_id in enumerate(results):
    taxi_id_position[ int(taxi_id[0]) ] = pos

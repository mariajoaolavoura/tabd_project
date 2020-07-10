import psycopg2
from postgis.psycopg import register

## Get the match between taxi's id in the db with that taxi's column in offsets.
## Create a dict { key=taxi_id_db, value=offsets_columns}
conn = psycopg2.connect("dbname=TABD user=postgres password=' ' ")
register(conn)
cursor_psql = conn.cursor()


# get 1st 10 taxis from Porto
sql = """
		select tr.taxi
		from cont_aad_caop2018 as caop, tracks as tr
		where caop.concelho='PORTO' and
			st_within(st_pointn(tr.proj_track,1), caop.proj_boundary) and
			tr.state='BUSY'
		order by tr.ts asc
		limit 10;
	"""

cursor_psql.execute(sql)
results = cursor_psql.fetchall()
taxis_porto = [ int(taxi[0]) for taxi in results ]

#    taxi   
# ----------
#  20000333 
#  20000450 
#  20000021 
#  20000850 
#  20000684 
#  20000199 
#  20000356 
#  20000474 
#  20000409 
#  20000598 
# (10 rows)


# get 1st 10 taxis from Lisbon
sql = """
		select tr.taxi
		from cont_aad_caop2018 as caop, tracks as tr
		where caop.concelho='LISBOA' and
			st_within(st_pointn(tr.proj_track,1), caop.proj_boundary) and
			tr.state='BUSY'
		order by tr.ts asc
		limit 10;
	"""
cursor_psql.execute(sql)
results = cursor_psql.fetchall()
taxis_lisbon = [ int(taxi[0]) for taxi in results ]

#    taxi  
# ---------
#  20093187
#  20092692
#  20091298
#  20090980
#  20091393
#  20093322
#  20091181
#  20092397
#  20091020
#  20090006
# (10 rows)
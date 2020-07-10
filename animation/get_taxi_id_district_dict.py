import psycopg2
from postgis.psycopg import register

conn = psycopg2.connect("dbname=TABD user=postgres password=' ' ")
register(conn)
cursor_psql = conn.cursor()

districts = [ 'BRAGA', 'PORTO', 'AVEIRO', 'COIMBRA', 'LISBOA', 'SANTARÉM']
taxi_id_district_dict = {}

for d in districts:
    sql =   """ select distinct taxi
                from tracks as tr, cont_aad_caop2018 as caop
                where caop.distrito='""" + d + """' and
                    st_within(st_pointn(tr.proj_track,1), caop.proj_boundary)
                order by 1;
            """
    cursor_psql.execute(sql)
    results = cursor_psql.fetchall()

    for value in results:
        taxi_id_district_dict[int(value[0])] = d

print(len(taxi_id_district_dict.keys()))
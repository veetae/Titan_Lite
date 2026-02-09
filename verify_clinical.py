import os, psycopg2
dsn = os.environ["DATABASE_URL"]
with psycopg2.connect(dsn) as c, c.cursor() as cur:
    for t in ("allergies","medications","labs","procedures","cardio_tests"):
        cur.execute(f"SELECT count(*) FROM titan.{t}")
        print(t, cur.fetchone()[0])

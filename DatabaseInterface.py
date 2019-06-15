import psycopg2
import subprocess
import os


class DatabaseConnector:
    def __init__(self):
        #proc = subprocess.Popen('heroku config:get DATABASE_URL -a url-scrambler', stdout=subprocess.PIPE, shell=True)
        #db_url = proc.stdout.read().decode('utf-8').strip() + '?sslmode=require'
        #self.conn = psycopg2.connect(db_url)

        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()

    def test(self):
        self.cur.execute("INSERT INTO urls (original, scrambled) VALUES ('test1', 'test2')")

        self.cur.execute("SELECT * FROM urls")
        print(self.cur.fetchall())

        self.conn.commit()

    def insert(self, original, scrambled):
        self.cur.execute("INSERT INTO urls (original, scrambled) VALUES ('{}', '{}')".format(original, scrambled))
        self.conn.commit()

    def select(self, scrambled):
        self.cur.execute("SELECT original FROM urls WHERE scrambled='{}'".format(scrambled))
        try:
            result = self.cur.fetchone()
            return result[0]    # trim
        except TypeError:
            return None


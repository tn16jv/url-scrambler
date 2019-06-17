import psycopg2
import subprocess
import os


class DatabaseConnector:
    def __init__(self, remote):
        if not remote:
            # these 3 lines are for local
            proc = subprocess.Popen('heroku config:get DATABASE_URL -a url-scrambler', stdout=subprocess.PIPE, shell=True)
            db_url = proc.stdout.read().decode('utf-8').strip() + '?sslmode=require'
            self.conn = psycopg2.connect(db_url)
        else:
            # these 3 lines are for remote
            DATABASE_URL = os.environ['DATABASE_URL']
            self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.cur = self.conn.cursor()

    def insert(self, original, scrambled, ip, id):
        self.cur.execute(
            "INSERT INTO urls (original, scrambled, ipv4, cookieId) VALUES ('{}', '{}', '{}', '{}')"
                .format(original, scrambled, ip, id))
        self.conn.commit()

    def select(self, scrambled):
        self.cur.execute(
            "SELECT original FROM urls WHERE scrambled='{}'"
                .format(scrambled))
        try:
            result = self.cur.fetchone()
            return result[0]    # trim
        except TypeError:
            return None

    def selectIdUrls(self, cookieId):
        self.cur.execute(
            "SELECT original, scrambled FROM urls WHERE cookieid='{}'".format(cookieId)
        )
        try:
            result = self.cur.fetchall()
            return result
        except TypeError:
            return None

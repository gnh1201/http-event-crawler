import sys
import os
import datetime
import socket
import json
import time

from flask import Flask
from flask import jsonify
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'your_userid'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your_password'
app.config['MYSQL_DATABASE_DB'] = 'your_dbname'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()

def main(args):
    try:
        last_id = getlastid()
    except:
        last_id = 0

    createindex(last_id)
    app.run(host='0.0.0.0')
    return 0

def setlastid(id):
    id = str(id)
    f = open("lastid", 'w')
    return f.write(id)

def getlastid():
    f = open("lastid", 'r')
    return int(f.read())

def sendMessageJsonOnSock(data):
   HOST = '127.0.0.1'
   PORT = 4050

   try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   except:
      return False

   try:
      sock.connect((HOST, PORT))
   except:
      return False

   bytesdata = json.dumps(data).encode("utf-8")
   print(bytesdata)

   sock.send(bytesdata)
   sock.close()

   time.sleep(0.03) # delay for guard

   return True

@app.route('/', methods=['GET', 'POST'])
def hello():
    return "Hello World!"

@app.route('/createindex/<start_id>', methods=['GET', 'POST'])
def createindex(start_id):

    # Initiate db connection
    cursor = conn.cursor()
    cursor.execute("select *, DATE_FORMAT(DATE_SUB(timestamp, INTERVAL 9 HOUR), '%Y-%m-%dT%TZ') as timestamp_s from http_event where id > {id}".format(id=start_id))
    rows = cursor.fetchall()

    # get field names
    fieldnames = [field[0] for field in cursor.description]

    # Fill index with posts from DB
    for row in rows:
        setlastid(row[0]) # set last id

        row = dict(zip(fieldnames, row))
        row['timestamp'] = time.mktime(row['timestamp'].timetuple())
        sendMessageJsonOnSock(row)
    try:
        return jsonify({"success": True})
    except:
        return 0

@app.route('/getevent/<event_id>', methods=['GET', 'POST'])
def getevent(event_id):
    cursor = conn.cursor()
    cursor.execute("select * from http_event where id = {id}".format(id=event_id))
    data = cursor.fetchone()

    fieldnames = [field[0] for field in cursor.description]
    data = dict(zip(fieldnames, data))

    try:
        return jsonify(row)
    except:
        return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

import datetime
import os
import random
import ssl
import datetime as dt

import gevent.pywsgi
from werkzeug.utils import secure_filename

from sqlalchemy import create_engine

from flask import Flask, flash, redirect, render_template, request
server = Flask(__name__)
#server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

with open("/specialist/credits") as f:
    login_str = f.readline()

with open("/specialist/keys") as f:
    temp = f.read().replace(" ", "").replace("'", "")
ENGINE = create_engine(f"postgresql+psycopg2://{login_str}@localhost:5432/specialist")
KEYS = temp.split(",")
del login_str, temp

@server.route('/', methods=["GET"])
@server.route('/home', methods=["GET"])
def index():
    collector = {
        'timestamp': dt.datetime.now(),
        'ip': request.remote_addr,
        "referrer": request.referrer,
    }
    temp = request.headers
    for i in temp.keys():
        collector[str(i).replace("-", "").lower()] = temp[i]
    
    keys = ', '.join([x for x in KEYS])
    values = ""
    for i in KEYS:
        if i in list(collector.keys()):
            values += "\'" + str(collector[i]) + "\',"
        else:
            values += "\'None\',"
    values = values[:-1]

    ENGINE.execute(f"INSERT INTO fingerprint ({keys}) VALUES ({values})")
    return render_template("index.html")

@server.route('/team')
def team():
    return render_template("team.html")

@server.route("/achiev")
def achiev():
    return render_template("achiev.html")

@server.route("/research")
def research():
    return render_template("research.html")

@server.route("/resources")
def resources():
    return render_template("resources.html")

if __name__ == '__main__':
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain("certificate.crt", "cert")
    app_server = gevent.pywsgi.WSGIServer(('0.0.0.0', 443), server, keyfile="cert", certfile='certificate.crt')
    app_server.serve_forever()

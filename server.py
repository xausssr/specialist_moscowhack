import datetime
import os
import random
import ssl
import datetime as dt

import gevent.pywsgi
from werkzeug.utils import secure_filename
import pickle
import pandas

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

with open('graphs/linked_results', 'rb') as f:
    LINKED_LIST = pickle.load(f)

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

@server.route("/roadmap", methods=["GET"])
def roadmap():
    if len(request.values) == 0:
        return render_template("roadmap_start.html")
    else:
        save_position = {
            "git": request.values["git"],
            "js": request.values["js"],
            "sql": request.values["sql"],
            "linux": request.values["linux"],
            "python": request.values["python"],
            "csharp": request.values["csharp"],
            "php": request.values["php"],
            "oop": request.values["oop"],
            "html": request.values["html"],
            "net": request.values["net"],
            }

        recommend_tree = get_tree(save_position)
        recommend_tree = color_map(recommend_tree, save_position)
        print(recommend_tree)
        with open(f"graphs/{recommend_tree}.txt") as f:
            graph_data = f.read()

        with open("graphs/first_part_roadmap.txt", "r") as f:
            first_part = f.read()
        
        with open("graphs/last_part_roadmap.txt", "r") as f:
            last_part = f.read()

        render_page = first_part + graph_data  + last_part
        mark = dt.datetime.now().timestamp()
        with open(f"templates/temp_graph_{mark}.html", 'w') as f:
            f.write(render_page)

        return render_template(f"temp_graph_{mark}.html", save_position=save_position)

def get_tree(save_position: dict) -> str:

    map_for_core = {
        "JavaScript": "js",
        "SQL": "sql",
        "Git": "git",
        "Python": "python",
        "PHP": "php",
        "MySQL": "mysql",
        "Linux": "linux",
        ".NET Framework": "net",
        "C#": "csharp",
        "HTML": "html",
        "ООП": "oop",
        "Linux": "linux"
    }

    map_for_pd = {}
    for key in map_for_core.keys():
        map_for_pd[map_for_core[key]] = key

    max_value = 0
    max_key = 0
    max_keys =[]
    for i in save_position.keys():
        if int(save_position[i]) > max_value:
            max_value = int(save_position[i])
            max_key = i

    for i in save_position.keys():
        if int(save_position[i]) == max_value:
            max_keys.append(i)

    if len(max_keys) == 1:
        for i in LINKED_LIST:
            if i[1].columns[0] == map_for_pd[max_key]:
                if map_for_core[i[1][i[1]["Percentage"] == i[1]["Percentage"].max()]["Skill"].values[0]] == "net":
                    return "git"
                else:
                    return map_for_core[i[1][i[1]["Percentage"] == i[1]["Percentage"].max()]["Skill"].values[0]]
    
    else:
        max_weight = 0
        max_weight_key = 0
        for idx, i in enumerate(LINKED_LIST):
            if i[1].columns[0] in [map_for_pd[x] for x in max_keys]:
                if int(i[0]) > max_weight:
                    max_weight = int(i[0])
                    max_weight_key = idx

        if map_for_core[LINKED_LIST[max_weight_key][1][LINKED_LIST[max_weight_key][1]["Percentage"] == LINKED_LIST[max_weight_key][1]["Percentage"].max()]["Skill"].values[0]] == "net":
            return "git"
        else:
            return map_for_core[LINKED_LIST[max_weight_key][1][LINKED_LIST[max_weight_key][1]["Percentage"] == LINKED_LIST[max_weight_key][1]["Percentage"].max()]["Skill"].values[0]]
    return "git"

def color_map(map_pos:str, save_position:dict) -> str:
    if int(save_position[map_pos]) < 3:
        return map_pos
    
    if int( 3 <= int(save_position[map_pos]) <= 6):
        return map_pos + "_2"

    if int( 7 <= int(save_position[map_pos])):
        return map_pos + "_3"

if __name__ == '__main__':
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain("certificate.crt", "cert")
    app_server = gevent.pywsgi.WSGIServer(('0.0.0.0', 443), server, keyfile="cert", certfile='certificate.crt')
    app_server.serve_forever()

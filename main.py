from flask import Flask, render_template
app = Flask(__name__)

import requests
url = 'https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv'
r = requests.get(url, allow_redirects=True)
open('data/germany_deliveries_timeseries_v2.tsv', 'wb').write(r.content)
url = 'https://raw.githubusercontent.com/ard-data/2020-rki-impf-archive/master/data/9_csv_v2/region_RP.csv'
r = requests.get(url, allow_redirects=True)
open('data/region_RP.csv', 'wb').write(r.content)

import pandas as pd
impfstoff = pd.read_table(
    'https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv',
    sep='\t')

from datetime import datetime
from datetime import date
current_week = int(datetime.today().isocalendar()[1])
week = 1

dosen = [[0] * 7] * 54
for i in range(54):
    dosen[i] = [i, 0, 0, 0, 0, 0, 0]

while week <= current_week:
    monday = date.fromisocalendar(2021, week, 1).strftime("%Y-%m-%d")
    sunday = date.fromisocalendar(2021, week, 7).strftime("%Y-%m-%d")
    print('CW ' + str(week) + ' ' + str(monday) + " - " + str(sunday))
    rp = impfstoff.loc[(impfstoff['date'] >= monday)
                       & (impfstoff['date'] <= sunday) &
                       (impfstoff['region'] == "DE-RP")]
    print(rp)
    comirnaty = int(rp.loc[(rp['impfstoff'] == "comirnaty"), ['dosen']].sum())
    moderna = int(rp.loc[(rp['impfstoff'] == "moderna"), ['dosen']].sum())
    astra = int(rp.loc[(rp['impfstoff'] == "astra"), ['dosen']].sum())
    johnson = int(rp.loc[(rp['impfstoff'] == "johnson"), ['dosen']].sum())
    dosen[week] = [
        week, comirnaty + int(dosen[week - 1][1]),
        moderna + int(dosen[week - 1][2]), astra + int(dosen[week - 1][3]), johnson + int(dosen[week - 1][4]),
        0, 0
    ]
    print (dosen[week])
    week += 1

dosen[0] = ['CW', 'Biontech', 'Moderna', 'Astra Zeneca', 'Johnson&Johnson', '', '']

from jinja2 import Environment, FileSystemLoader
import os
loader = FileSystemLoader(searchpath='templates')
env = Environment(loader=loader)
template = env.get_template('template.html')
filename = os.path.join('static', 'index.html')
with open(filename, 'w') as fh:
    fh.write(template.render(var_dosen=dosen, ))

@app.route('/')
def serving_html():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

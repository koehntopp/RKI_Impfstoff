from flask import Flask, render_template
app = Flask(__name__)

import pandas as pd
impfstoff = pd.read_table('https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv', sep= '\t')

from datetime import datetime
from datetime import date
current_week = int(datetime.today().isocalendar()[1])
week = 1

dosen = [[0]*7]*54
for i in range (54):
   dosen[i] = [i,0,0,0,0,0,0]
dosen[0] = ['CW', 'Biontech', 'Moderna', 'Astra Zeneca', '', '', '']

while week <= current_week:
  monday = date.fromisocalendar(2021, week, 1).strftime("%Y-%m-%d")
  sunday = date.fromisocalendar(2021, week, 7).strftime("%Y-%m-%d")
  rp = impfstoff.loc[(impfstoff['date'] >= monday) & (impfstoff['date'] <= sunday)]
  comirnaty = int(rp.loc[(rp['impfstoff'] == "comirnaty"), ['dosen']].sum())
  moderna = int(rp.loc[(rp['impfstoff'] == "moderna"), ['dosen']].sum())
  astra = int(rp.loc[(rp['impfstoff'] == "astra"), ['dosen']].sum())
  dosen[week] = [week, comirnaty, moderna, astra, 0, 0, 0]
  week += 1

print(dosen)

from jinja2 import Environment, FileSystemLoader
import os
loader = FileSystemLoader(searchpath='templates')
env = Environment( loader = loader )
template = env.get_template('template.html')
filename = os.path.join('static', 'index.html')
with open(filename, 'w') as fh:
  fh.write(template.render(
    var_dosen = dosen,
  ))

@app.route('/')
def serving_html():
  return app.send_static_file('index.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
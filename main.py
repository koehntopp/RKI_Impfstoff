from flask import Flask, render_template
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

from datatable import dt, fread, f, by
impfstoff = fread("https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv")

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
  rp = impfstoff[(f.date >= monday) & (f.date <= sunday) & (f.region == "DE-RP"), :]
  comirnaty = int(rp[(f.impfstoff == "comirnaty"), dt.sum(f.dosen)][0, 0])
  moderna = int(rp[(f.impfstoff == "moderna"), dt.sum(f.dosen)][0, 0])
  astra = int(rp[(f.impfstoff == "astra"), dt.sum(f.dosen)][0, 0])
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

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
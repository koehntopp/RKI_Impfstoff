import requests
url = 'https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv'
r = requests.get(url, allow_redirects=True)
open('data/germany_vaccinations_timeseries_v2', 'wb').write(r.content)

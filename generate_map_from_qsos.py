import sqlite3

#get last 50 QSOs from sqlite database
db = sqlite3.connect('qso_database.sqlite')
c = db.cursor()
c.execute('''SELECT call FROM current_qsos ORDER BY timestamp DESC LIMIT 50''')
calls = [entry[0] for entry in c.fetchall()]

#get list over prefixes and lat/lon from clublog xml file
#obtained from https://clublog.org/cty.php?api=API_KEY
import xml.etree.cElementTree as ET
tree = ET.parse('cty.xml')
ns = {'fjas': 'https://clublog.org/cty/v1.2'}
results = tree.findall("./fjas:prefixes/fjas:prefix", ns)
prefixes = {}
for res in results:
    prefix = res.findall("fjas:call", ns)[0].text
    try:
        longitude = res.findall("fjas:long", ns)[0].text
        latitude = res.findall("fjas:lat", ns)[0].text
    except:
        continue
    prefixes[prefix] = (latitude, longitude)

#get possible prefix lengths
import numpy as np
prefix_lens = np.array([len(prefix) for prefix in list(prefixes)])
max_prefix_length = np.max(prefix_lens)
min_prefix_length = np.min(prefix_lens)

#create map
import cartopy
import cartopy.feature as cpf
import cartopy.crs as ccrs

import matplotlib.pyplot as plt
ax = plt.figure().gca(projection=cartopy.crs.PlateCarree())
ax.add_feature(cpf.LAND)
#ax.set_global()
qth_coord = [63.42, 10.39]
plt.plot(qth_coord[1], qth_coord[0], 'o', color='black')

#match the QSO calls against prefix database, find latlon, plot in map
for i, call in enumerate(calls):
    #try with largest potential prefix part first and gradually reduce until match (probably exists a more efficient way to do this, construct a decision tree or something)
    latlon = None
    for prefix_len in range(max_prefix_length, min_prefix_length-1, -1):
        prefix_cand = call[:prefix_len]
        try:
            latlon = prefixes[prefix_cand]
            break
        except:
            continue
    print(call, latlon)

    progr = (len(calls) - i)/(1.0*len(calls))
    print(progr)
    color = 'black'
    xs = [qth_coord[1], float(latlon[1])]
    ys = [qth_coord[0], float(latlon[0])]
    if i == 0:
        color='red'
        plt.plot(xs, ys, color=color, transform=ccrs.Geodetic())
    else:
        color='black'

    plt.plot(xs[1], ys[1], 'o', color=color, alpha=progr)



plt.show()

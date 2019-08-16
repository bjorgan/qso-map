import sqlite3
import argparse
import xml.etree.cElementTree as ET
import numpy as np
import cartopy
import cartopy.feature as cpf
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import json
import random
import matplotlib.cm

#parse arguments
parser = argparse.ArgumentParser(description='Generate map over last N QSOs from database on hybelpc.')
parser.add_argument('--db-file', metavar='db_file', type=str, default='qso_database.sqlite',
        help='Path to sqlite QSO database.')
parser.add_argument('--prefix-xml-file', metavar='prefix_xml_file', type=str, default='cty.xml',
        help='Path to XML file containing prefix-country mapping from ClubLog.')
parser.add_argument('--output-filename', metavar='output_filename', type=str, default='map.png',
        help='Output filename.')
args = parser.parse_args()

#get last 50 QSOs from sqlite database
db = sqlite3.connect(args.db_file)
c = db.cursor()
c.execute('''SELECT call FROM current_qsos ORDER BY timestamp DESC LIMIT 50''')
calls = [entry[0] for entry in c.fetchall()]
c.execute('''SELECT operator FROM current_qsos ORDER BY timestamp DESC LIMIT 50''')
operators = [entry[0] for entry in c.fetchall()]

#get list over prefixes and lat/lon from clublog xml file
#obtained from https://clublog.org/cty.php?api=API_KEY
tree = ET.parse(args.prefix_xml_file)
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
prefix_lens = np.array([len(prefix) for prefix in list(prefixes)])
max_prefix_length = np.max(prefix_lens)
min_prefix_length = np.min(prefix_lens)

#create map
ax = plt.figure().gca(projection=cartopy.crs.PlateCarree())
ax.add_feature(cpf.LAND)
#ax.set_global()
qth_coord = [63.42, 10.39]
plt.plot(qth_coord[1], qth_coord[0], 'o', color='black', label="LA1K")

# Assign colors based on tab10 color map. Pseudo-consistent colors achieved with enumeration
colors = {}
cmap = matplotlib.cm.get_cmap('tab10')
for i, op in enumerate(np.sort(np.unique(operators))):
    colors[op] = cmap(i)


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

    color = 'black'
    xs = [qth_coord[1], float(latlon[1])]
    ys = [qth_coord[0], float(latlon[0])]
    if i == 0:
        color='red'
        plt.plot(xs, ys, color=color, transform=ccrs.Geodetic())
    else:
        color='black'
        
        plt.plot(xs[1], ys[1], 'o', color=colors[operators[i]], label=operators[i])

# Add legend with labels (for each unique operator)
handles, labels = plt.gca().get_legend_handles_labels()
_, indices = np.unique(labels, return_index=True)
handles = np.array(handles)[indices]
labels = np.array(labels)[indices]
plt.legend(handles, labels)
plt.show()

plt.savefig(args.output_filename, bbox_inches='tight', dpi=300)

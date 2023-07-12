# %%
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from shapely.geometry import Point
import geopandas as gpd
import folium

from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area
from geovoronoi import voronoi_regions_from_coords, points_to_coords

# %%
url = "https://en.wikipedia.org/wiki/List_of_Montreal_Metro_stations"
stations = pd.read_html(url)[1]

# %%
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find_all('table')[1]

# %%
links = []
for tr in table.findAll("tr"):
  trs = tr.findAll("th")
  for each in trs:
    try:
      link = each.find('a')['href']
      links.append(link)
    except:
      pass
stations['Link']=links[1:]

# %%
base_url = 'https://en.wikipedia.org'
def get_coords(link):
  r = requests.get(base_url + link)
  soup = BeautifulSoup(r.text, 'html.parser')
  coordstring = soup.find(class_="geo").text.strip()
  tuplestring = tuple(map(float, coordstring.split(';')))
  return (tuplestring[1], tuplestring[0])
stations['coords'] = stations['Link'].apply(get_coords)

# %%
stations['coords']

# %%
canada = gpd.read_file('./lpr_000b16a_e.shp')
canada = canada.to_crs('WGS84')

# %%
quebec = canada[canada['PRENAME'] == 'Quebec']
quebecgeo = quebec.iloc[0]['geometry']
montrealgeo = list(quebecgeo.geoms)[3]


# %%
fig, ax = plt.subplots(figsize=(12,12))
quebec.plot(ax=ax)
ax.set_xlim(-73.75,-73.472)
ax.set_ylim(45.398,45.623)

for i in range(len(stations)):
  d = stations.iloc[i]
  cds = d['coords']
  ax.plot(cds[0], cds[1],  marker='o', markersize=8,color='C1', zorder=10)

plt.show()

# %%
for i,row in stations.iterrows():
    print(row)

# %%
if not quebecgeo.is_valid or quebecgeo.is_empty:
 print('Invalid Geometry')
else:
 print('Geometry Valid')
 
for i, row in stations.iterrows():
  cds = row['coords']
  name = row['Name']
  p = Point(cds[0], cds[1])
  if not quebecgeo.contains(p):
     print(f'{name} ||| OUTSIDE BOUNDARY')

# %%
arcords = np.array(list(map(list, stations['coords'].tolist())))
# arcords = np.roll(arcords,1,axis=1)
region_polys, region_pts = voronoi_regions_from_coords(arcords,quebecgeo)
fig, ax = plt.subplots(figsize=(12,12))
plot_voronoi_polys_with_points_in_area(ax, quebecgeo, region_polys, arcords, region_pts)
ax.set_xlim(-73.75,-73.472)
ax.set_ylim(45.398,45.623)

plt.show(block=True)
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Proj
from shapely.geometry import Point

fig = plt.figure(figsize = (15, 10))
montreal = gpd.read_file("geobase_mtl.shp")

inProj = Proj(init='epsg:32188')
for i in range(4):
    ax = fig.add_subplot(2, 4, i + 1)
    montreal.plot(ax = ax, color = 'gray', linewidth = 0.3)
    if i == 0:
        data = pd.read_csv('OD_2018-04.csv')
        for month in ['05', '06', '07', '08', '09', '10', '11']:
            data_add = pd.read_csv('OD_2018-{}.csv'.format(month))
            data = pd.concat([data, data_add], ignore_index=True, sort=False)
    elif i == 1:
        data = pd.read_csv('OD_2019-04.csv')
        for month in ['05', '06', '07', '08', '09', '10']:
            data_add = pd.read_csv('OD_2019-{}.csv'.format(month))
            data = pd.concat([data, data_add], ignore_index=True, sort=False)
    elif i == 2:
        data = pd.read_csv('OD_2020.csv')
    elif i == 3:
        data = pd.read_csv('2021_donnees_ouvertes.csv')
    station = pd.read_csv('Stations_20{}.csv'.format(18 + i))

    if i == 3:
        df = data.groupby(['emplacement_pk_end'])['emplacement_pk_end'].count().reset_index(name = 'count')
    else:
        df = data.groupby(['end_station_code'])['end_station_code'].count().reset_index(name = 'count')
    if i == 1:
        merged = station.set_index('Code').join(df.set_index('end_station_code'))
    elif i == 3:
        merged = station.set_index('pk').join(df.set_index('emplacement_pk_end'))
    else:
        merged = station.set_index('code').join(df.set_index('end_station_code'))
    merged = merged.reset_index()
    n = station['longitude'].values.shape[0]
    x2,y2 = inProj(station['longitude'].values, station['latitude'].values)
    data = merged
    data['latitude'] = x2
    data['longitude'] = y2
    geometry = [Point(xy) for xy in zip(data['latitude'], data['longitude'])]
    geo_df = gpd.GeoDataFrame(data, crs = {'init': 'epsg:32188'}, geometry = geometry)

    geo_df.plot('count', cmap = 'Reds', ax = ax, markersize = 15,
                zorder = 52, legend = True, legend_kwds = {'shrink': 0.5, 'label': 'Number of trips'})

    ax.set(xlim=[287000, 305500], ylim=[5030000, 5063000])
    plt.title('20{}'.format(18 + i))
    plt.xticks([])
    plt.yticks([])
    for _, spine in ax.spines.items():
        spine.set_visible(True)
plt.show()

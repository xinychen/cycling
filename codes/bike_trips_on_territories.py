import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from pyproj import Proj
from shapely.geometry import Point

plt.rcParams['font.size'] = 12
fig = plt.figure(figsize = (15, 11))
fig.subplots_adjust(hspace = 0, wspace = 0)
territories = gpd.read_file('quartier_limite.shp')

inProj = Proj(init = 'epsg:32188')
for i in range(4):
    ax = fig.add_subplot(2, 4, i + 1)
    
    ## Read bike trip data for each year
    if i == 0: # 2018
        data = pd.read_csv('OD_2018-04.csv')
        for month in ['05', '06', '07', '08', '09', '10', '11']:
            data_add = pd.read_csv('OD_2018-{}.csv'.format(month))
            data = pd.concat([data, data_add], ignore_index = True, sort = False)
    elif i == 1: # 2019
        data = pd.read_csv('OD_2019-04.csv')
        for month in ['05', '06', '07', '08', '09', '10']:
            data_add = pd.read_csv('OD_2019-{}.csv'.format(month))
            data = pd.concat([data, data_add], ignore_index = True, sort = False)
    elif i == 2: # 2020
        data = pd.read_csv('OD_2020.csv')
    elif i == 3: # 2021
        data = pd.read_csv('2021_donnees_ouvertes.csv')
    station = pd.read_csv('Stations_20{}.csv'.format(i + 18))
    
    ## Match the bike trips to the bikeshare stations
    if i == 3: # 2021
        df = data.groupby(['emplacement_pk_start'])['emplacement_pk_start'].count().reset_index(name = 'count')
    else: # 2018, 2019, 2020
        df = data.groupby(['start_station_code'])['start_station_code'].count().reset_index(name = 'count')
    if i == 1: # 2019
        merged = station.set_index('Code').join(df.set_index('start_station_code'))
    elif i == 3: # 2021
        merged = station.set_index('pk').join(df.set_index('emplacement_pk_start'))
    else:
        merged = station.set_index('code').join(df.set_index('start_station_code'))
    merged = merged.reset_index()
    n = station['longitude'].values.shape[0]
    x2, y2 = inProj(station['longitude'].values, station['latitude'].values)
    data = merged
    data['latitude'] = x2
    data['longitude'] = y2
    
    ## Create the `.shp` file of bikeshare stations and cover the bike trips
    geometry = [Point(xy) for xy in zip(data['latitude'], data['longitude'])]
    geo_df = gpd.GeoDataFrame(data, crs = {'init': 'epsg:32188'}, geometry = geometry)
    gdf = gpd.sjoin(geo_df, territories, op = 'contains').groupby('name').sum()
    
    ## Plot the bike trips on the road network
    if i == 3:
        gdf.plot('count', cmap = 'Reds', ax = ax, markersize = 15, vmin = 0, vmax = 25000, 
                    zorder = 52, legend = True, legend_kwds = {'shrink': 0.5, 'label': 'Number of trips'})
    else:
        gdf.plot('count', cmap = 'Reds', ax = ax, markersize = 15, vmin = 0, vmax = 25000, zorder = 52)
    ax.set(xlim = [287000, 305500], ylim = [5030000, 5063000])
    plt.title('20{}'.format(18 + i))
    plt.xticks([])
    plt.yticks([])
    for _, spine in ax.spines.items():
        spine.set_visible(True)
    
    ## Zoom in the road network
#     ax = fig.add_subplot(2, 4, i + 5)
#     if i == 3:
#         geo_df.plot('count', cmap = 'Reds', ax = ax, markersize = 15, vmin = 0, vmax = 25000, 
#                     zorder = 52, legend = True, legend_kwds = {'shrink': 0.5, 'label': 'Number of trips'})
#     else:
#         geo_df.plot('count', cmap = 'Reds', ax = ax, markersize = 15, vmin = 0, vmax = 25000, zorder = 52)
#     ax.set(xlim = [293600, 302600], ylim = [5033000, 5049000])
#     plt.title('20{}'.format(18 + i))
#     plt.xticks([])
#     plt.yticks([])
#     for _, spine in ax.spines.items():
#         spine.set_visible(True)
fig.savefig("bikeshare_pickup_trips_territories.png", bbox_inches = "tight")
plt.show()

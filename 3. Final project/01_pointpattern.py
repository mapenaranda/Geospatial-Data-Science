# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 11:10:32 2023

@author: Mario
"""

import numpy as np
import pandas as pd
import geopandas as gpd

import osmnx as ox
import pysal

import seaborn as sns
import contextily as ctx
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

from sklearn.cluster import DBSCAN

#Let's read the files

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/final_file_gds.csv")

ne = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/barrios.geojson")

#Filter neighborhoods by comuna

ne['COMUNA'] = ne['COMUNA'].astype('float')

ne = ne[ne['COMUNA'] <= 16]

#ne = ne.to_crs('EPSG:3857')

#Determine the limits of the data

limit = ox.geocode_to_gdf('Medellin, Colombia')

#Clean the coordinates considering the bbox method

df = df[df['latitude'] >= limit['bbox_south'].iloc[0]]
df = df[df['latitude'] <= limit['bbox_north'].iloc[0]]

df = df[df['longitude'] <= limit['bbox_east'].iloc[0]]
df = df[df['longitude'] >= limit['bbox_west'].iloc[0]]

#Now, create a geodataframe to add geometry and spatialty

geo = gpd.points_from_xy(x=df['longitude'], y=df['latitude'], crs='EPSG:4326')

gdf = gpd.GeoDataFrame(df, geometry=geo)

#gdf = gdf.to_crs('EPSG:3857')


#Compute a spatial join to capture attributes from the neighborhoods

sjoined = gpd.sjoin(gdf, ne, how='inner')

#################       CENTROGRAPHY          #################################

#Compute new variable x, y with the amount of the projected coordinate

from shapely import wkt

gdf_2 = gdf.to_crs('EPSG:3857')

gdf_2['geometry'] = gdf_2.geometry.apply(lambda x: wkt.dumps(x))

gdf_2['geometry'] = gdf_2['geometry'].astype('str')

rep = {'POINT':'', '(': '', ')': ''}

gdf_2['geometry'] = gdf_2['geometry'].apply(lambda x: x.replace('POINT', ''))

gdf_2['geometry'] = gdf_2['geometry'].apply(lambda x: x.replace('(', ''))

gdf_2['geometry'] = gdf_2['geometry'].apply(lambda x: x.replace(')', ''))

gdf_2[['not', 'x', 'y']] = gdf_2['geometry'].str.split(' ', expand=True)

df['x'] = gdf_2['x']

df['y'] = gdf_2['y']



df['x'] = df['x'].astype(float)

df['y'] = df['y'].astype(float)



from pointpats import centrography

mean_center = centrography.mean_center(df[['x', 'y']])

med_center = centrography.euclidean_median(df[['x', 'y']])

st_dist = centrography.std_distance(df[['x', 'y']])

major, minor, rotation = centrography.ellipse(df[['x', 'y']])

##### Plot centrography chart ########

from matplotlib.patches import Ellipse

f, ax = plt.subplots(1, figsize=(9,9))

ax.scatter(df['x'], df['y'], s=0.75)
ax.scatter(*mean_center, color='red', marker='x', label='Mean Center')
ax.scatter(*med_center, color='limegreen', marker='o', label='Median Center')

ellipse = Ellipse(xy=mean_center, width=major*2, height=minor*2, angle=np.rad2deg(rotation), facecolor='none',
                  edgecolor='red', linestyle='--', label='Std. Ellipse')

ax.add_patch(ellipse)

ax.legend()

ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

plt.title("Crashes' centrography in Medellin 2016-2019")

scale = ScaleBar(1, 'm', location="lower right", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()


#################       KERNEL DENSITY ESTIMATION (KDE)          #################################

f, ax = plt.subplots(1, figsize=(9,9))

sns.kdeplot(x=df['x'], y=df['y'], n_levels=30, fill=True, alpha=0.55, cmap='viridis_r')

ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

plt.title('KDE for crashes in Medellin 2016-2019 (30 levels)')

scale = ScaleBar(1, 'm', location="lower right", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

ax.set_axis_off()


#################       RIPLEY'S TECHNIQUES          #################################

from pointpats import distance_statistics, QStatistic, random, PointPattern

#### Plot G function ####

coordinates = df[['x', 'y']].sample(1000).values

g_test = distance_statistics.g_test(coordinates, support=40, keep_simulations=True)

f, ax = plt.subplots(1, 2, figsize=(9,3), gridspec_kw=dict(width_ratios=(6,3)))

ax[0].plot(g_test.support, g_test.simulations.T, color='k', alpha=0.01)

ax[0].plot(g_test.support, np.median(g_test.simulations, axis=0), color='cyan', label='median simulation')

ax[0].plot(g_test.support, g_test.statistic, label='observed', color='red')

ax[0].set_xlabel('distance')
ax[0].set_ylabel('% of nearest neighbor/distances shorter')
ax[0].legend()
ax[0].set_xlim(0,2000)

ax[0].set_title(r"Ripley's $G(d)$ function")

ax[1].scatter(*coordinates.T)

ax[1].set_xticks([])
ax[1].set_yticks([])
ax[1].set_xticklabels([])
ax[1].set_yticklabels([])
ax[1].set_title('Pattern')
f.tight_layout()

plt.show()

#### Plot F function ####

f_test = distance_statistics.f_test(coordinates, support=40, keep_simulations=True)

f, ax = plt.subplots(1, 2, figsize=(9, 3), gridspec_kw=dict(width_ratios=(6,3)))

ax[0].plot(f_test.support, f_test.simulations.T, color='k', alpha=0.01)

ax[0].plot(f_test.support, np.median(f_test.simulations, axis=0), color='cyan', label='median simulation')

ax[0].plot(f_test.support, f_test.statistic, label='observed', color='red')

ax[0].set_xlabel('distance')
ax[0].set_ylabel('% of nearest point in pattern\ndistances shorter')
ax[0].legend()
ax[0].set_xlim(0,2000)
ax[0].set_title(r"Ripley's $F(d)$ function")

ax[1].scatter(*coordinates.T)

ax[1].set_xticks([])
ax[1].set_yticks([])
ax[1].set_xticklabels([])
ax[1].set_yticklabels([])
ax[1].set_title('Pattern')
f.tight_layout()

plt.show()


######################      DBSCAN   ########################

clusterer = DBSCAN(eps=5, min_samples=10)

clusterer.fit(df[['x', 'y']])

lbls = pd.Series(clusterer.labels_, index=df.index)


f, ax = plt.subplots(1, figsize=(9, 9))

noise = df.loc[lbls==-1, ['x', 'y']]

ax.scatter(noise['x'], noise['y'], c='grey', s=5, linewidth=0)

ax.scatter(df.loc[df.index.difference(noise.index), 'x'],
           df.loc[df.index.difference(noise.index), 'y'],
           c='red', linewidth=0)

ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

ax.set_axis_off()

plt.title("DBSCAN Clustering Crashes 2016-2019 (r = 5m, sample=10)")

scale = ScaleBar(1, 'm', location="lower right", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()



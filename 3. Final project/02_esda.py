# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 12:55:51 2023

@author: Mario
"""

import osmnx as ox
import seaborn as sns
import pandas as pd

from pysal.lib import weights
from pysal.explore import esda
from pysal.viz import splot
from splot.esda import plot_moran
from splot.esda import plot_local_autocorrelation

import geopandas as gpd
import numpy as np

import contextily as ctx
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

import math

circumference = 6378137

def circle_distance(latlong_a, latlong_b):
    lat1, lon1 = latlong_a
    lat2, lon2 = latlong_b
    
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
            math.sin(dLon / 2) * math.sin(dLon / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = circumference * c
    
    return d

X = -75.5772
Y = 6.2173

dx = circle_distance((X, Y), (X + 1, Y))


#import the dataset to work with

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/final_file_gds.csv")

ne = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/barrios.geojson")

road = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/barrios2.geojson")

#filter road dataset to join with nighborhoods

road = road[['OBJECTID', 'road_length(m)', 'road_density']]

ne = ne.merge(road, on='OBJECTID', how='left')

#Filter neighborhoods by comuna

ne['COMUNA'] = ne['COMUNA'].astype('float')

ne = ne[ne['COMUNA'] <= 16]

ne = ne.to_crs('EPSG:4326')

#Filter by severity

df = df[df['injured'] == 1]

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


#Create a GeoDataFrame to aggregate crashes within neigborhoods regarding the severity

injured = gpd.sjoin(gdf, ne, how='left')

injured = injured.drop(['index_right', 'SECTOR', 'INDICADOR_UR', 'SHAPE__Area', 'SHAPE__Length'], axis=1)

injured.set_index('filed_id', inplace=True)

##############################    CHOROPLETS ####################################



#Number of crashes within the neighborhoods

number_crash = injured.groupby('OBJECTID')['year'].count()

number_crash.rename('number_crash', inplace=True)

ne = ne.merge(number_crash, on='OBJECTID', how='inner')

#Choroplet for number of crashes

f, ax = plt.subplots(1, figsize=(9,9))

ax = ne.plot(column='number_crash', scheme='natural_breaks', legend=True, ax=ax, cmap='plasma')

ctx.add_basemap(ax, crs=ne.crs, source=ctx.providers.Stamen.TonerLite)

ax.set_axis_off()

f.suptitle('Count of crashes by neigborhood in Medellin 2016-2019')

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()

#Save a table considering the total of crashes by neighborhood

t_number_crash = injured.groupby(['NOMBRE_COMUNA', 'NOMBRE_BARRIO'])['year'].count().sort_values(ascending=False).head(10)

t_number_crash.rename('number_crash', inplace=True)





#Average vehicles involved in crashes by neighborhoods

aver_veh = injured.groupby('OBJECTID')['number_veh'].mean()

aver_veh.rename('aver_veh', inplace=True)

ne = ne.merge(aver_veh, on='OBJECTID', how='inner')


#Choroplet for the average number of vehicles involved in crashes

f, ax = plt.subplots(1, figsize=(9,9))

ax = ne.plot(column='aver_veh', scheme='natural_breaks', legend=True, ax=ax, cmap='plasma')

ctx.add_basemap(ax, crs=ne.crs, source=ctx.providers.Stamen.TonerLite)

ax.set_axis_off()

f.suptitle('Average amount of vehicles involved in crashes by neigborhood in Medellin 2016-2019')

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()

#Save a table considering the average number vehicles in crashes by neighborhood

t_aver_veh = ne.sort_values(by=['aver_veh'], ascending=False).head(10)

t_aver_veh = t_aver_veh[['NOMBRE_COMUNA', 'NOMBRE_BARRIO', 'aver_veh']]



#Number of crashes that involved a bicycle

number_bici = injured.groupby('OBJECTID')['bici_involved'].sum()

ne = ne.merge(number_bici, on='OBJECTID', how='inner')

#Choroplet for crashes that involved bicycles

f, ax = plt.subplots(1, figsize=(9,9))

ax = ne.plot(column='bici_involved', scheme='natural_breaks', legend=True, ax=ax, cmap='Reds')

ctx.add_basemap(ax, crs=ne.crs, source=ctx.providers.Stamen.TonerLite)

ax.set_axis_off()

f.suptitle('Count of crashes that involved a bicyle by neigborhood in Medellin 2016-2019')

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()

#Save a table considering the crashes that involved bicycles

t_number_bici = ne.sort_values(by=['bici_involved'], ascending=False).head(10)

t_number_bici = t_number_bici[['NOMBRE_COMUNA', 'NOMBRE_BARRIO', 'bici_involved']]



#Number of crashes that involved a motorcycle

number_moto = injured.groupby('OBJECTID')['moto_involved'].sum()

ne = ne.merge(number_moto, on='OBJECTID', how='inner')

#Choroplet for crashes that involved motorcycles

f, ax = plt.subplots(1, figsize=(9,9))

ax = ne.plot(column='moto_involved', scheme='natural_breaks', legend=True, ax=ax, cmap='Oranges')

ctx.add_basemap(ax, crs=ne.crs, source=ctx.providers.Stamen.TonerLite)

ax.set_axis_off()

f.suptitle('Count of crashes that involved a motorcycle by neigborhood in Medellin 2016-2019')

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()

#Save a table considering the crashes that involved motorcycles by neighborhood

t_number_moto = ne.sort_values(by=['moto_involved'], ascending=False).head(10)

t_number_moto = t_number_moto[['NOMBRE_COMUNA', 'NOMBRE_BARRIO', 'moto_involved']]




#Number of crashes that involved an automobiles

number_auto = injured.groupby('OBJECTID')['auto_involved'].sum()

ne = ne.merge(number_auto, on='OBJECTID', how='inner')

#Choroplet for crashes that involved automobiles

f, ax = plt.subplots(1, figsize=(9,9))

ax = ne.plot(column='auto_involved', scheme='natural_breaks', legend=True, ax=ax, cmap='Greys')

ctx.add_basemap(ax, crs=ne.crs, source=ctx.providers.Stamen.TonerLite)

ax.set_axis_off()

f.suptitle('Count of crashes that involved an automobile by neigborhood in Medellin 2016-2019')

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()

#Save a table considering the crashes that involved an automobiles

t_number_auto = ne.sort_values(by=['auto_involved'], ascending=False).head(10)

t_number_auto = t_number_auto[['NOMBRE_COMUNA', 'NOMBRE_BARRIO', 'auto_involved']]



#Length of the road network in the area of study

f, ax = plt.subplots(1, figsize=(9,9))

ax = ne.plot(column='road_length(m)', scheme='natural_breaks', legend=True, ax=ax, cmap='BuGn')

ctx.add_basemap(ax, crs=ne.crs, source=ctx.providers.Stamen.TonerLite)

ax.set_axis_off()

f.suptitle('Total length of the road network (m) by neigborhood in Medellin')

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()

#Save a table considering the road length in the neighborhood

t_total_length = ne.sort_values(by=['road_length(m)'], ascending=False).head(10)

t_total_length = t_total_length[['NOMBRE_COMUNA', 'NOMBRE_BARRIO', 'road_length(m)']]




########################### SPATIAL AUTOCORRELATION ############################

#Take out of the analysis the islands within Medellin
w_queen = weights.Queen.from_dataframe(ne, idVariable='NOMBRE_BARRIO')

islands = w_queen.islands

ne_sa = ne[(ne['NOMBRE_BARRIO'] != 'Aures No. 2') &
           (ne['NOMBRE_BARRIO'] != 'Calasanz Parte Alta') &
           (ne['NOMBRE_BARRIO'] != 'El Rincón') &
           (ne['NOMBRE_BARRIO'] != 'La Avanzada')]

ne_sa = ne_sa.to_crs('EPSG:3857')

#Recompute the Queen matrix
w_queen = weights.Queen.from_dataframe(ne_sa, idVariable='NOMBRE_BARRIO')

#We have to standarize the matrix to compute the proportion of neighbors values
w_queen.transform = 'R'

#Then compute the spatial lag for the important variables for spatial analysis
ne_sa['w_number_crash'] = weights.lag_spatial(w_queen, ne_sa['number_crash'])

ne_sa['w_aver_veh'] = weights.lag_spatial(w_queen, ne_sa['aver_veh'])

ne_sa['w_bici_involved'] = weights.lag_spatial(w_queen, ne_sa['bici_involved'])

ne_sa['w_moto_involved'] = weights.lag_spatial(w_queen, ne_sa['moto_involved'])

#Compute some tables to easily explain the results
sl_number_crash = ne_sa[['NOMBRE_BARRIO', 'NOMBRE_COMUNA', 'number_crash', 'w_number_crash']].sort_values(by=['w_number_crash'], ascending=False).head(10)

sl_aver_veh = ne_sa[['NOMBRE_BARRIO', 'NOMBRE_COMUNA', 'aver_veh', 'w_aver_veh']].sort_values(by=['w_aver_veh'], ascending=False).head(10)

sl_bici_involved = ne_sa[['NOMBRE_BARRIO', 'NOMBRE_COMUNA', 'bici_involved', 'w_bici_involved']].sort_values(by=['w_bici_involved'], ascending=False).head(10)

sl_moto_involved = ne_sa[['NOMBRE_BARRIO', 'NOMBRE_COMUNA', 'moto_involved', 'w_moto_involved']].sort_values(by=['w_moto_involved'], ascending=False).head(10)


#Compute the standarize of the spatial lag to easily compare and identify outliers

ne_sa['number_crash_std'] = (ne_sa['number_crash'] - ne_sa['number_crash'].mean())/ne_sa['number_crash']

ne_sa['ave_veh_std'] = (ne_sa['aver_veh'] - ne_sa['aver_veh'].mean())/ne_sa['aver_veh']

ne_sa['moto_involved_std'] = (ne_sa['moto_involved'] - ne_sa['moto_involved'].mean())/ne_sa['moto_involved']

#Compute the standarize spatial lag
ne_sa['w_number_crash_std'] = weights.lag_spatial(w_queen, ne_sa['number_crash_std'])

ne_sa['w_aver_veh_std'] = weights.lag_spatial(w_queen, ne_sa['ave_veh_std'])

ne_sa['w_moto_involved_std'] = weights.lag_spatial(w_queen, ne_sa['moto_involved_std'])




######### PLOT THE SPATIAL LAGS ###########

#Count of crashes
f, ax = plt.subplots()

ne_sa.plot(column='w_number_crash_std', cmap='viridis', scheme='naturalbreaks', edgecolor='white',
           linewidth=0., alpha=0.75, legend=True, ax=ax)

ax.set_axis_off()
ax.set_title('Count of crashes in Medellin 2016-2019 - Standardized Spatial Lag')

ctx.add_basemap(ax, crs=ne_sa.crs, source=ctx.providers.Stamen.TonerLite)

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()

#Average of vehicles involved in the crash
f, ax = plt.subplots()

ne_sa.plot(column='w_aver_veh_std', cmap='Blues', scheme='naturalbreaks', edgecolor='white',
           linewidth=0., alpha=0.75, legend=True, ax=ax)

ax.set_axis_off()
ax.set_title('Average vehicles involved in crashes in Medellin 2016-2019 - Standardized Spatial Lag ')

ctx.add_basemap(ax, crs=ne_sa.crs, source=ctx.providers.Stamen.TonerLite)

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()


#Number of crashes that involved bicycles
f, ax = plt.subplots()

ne_sa.plot(column='w_bici_involved', cmap='plasma', scheme='naturalbreaks', edgecolor='white',
           linewidth=0., alpha=0.75, legend=True, ax=ax)

ax.set_axis_off()
ax.set_title('Bicycles involved in crashes in Medellin 2016-2019 - Spatial Lag ')

ctx.add_basemap(ax, crs=ne_sa.crs, source=ctx.providers.Stamen.TonerLite)

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()


#Motorcycles involved in crashes
f, ax = plt.subplots()

ne_sa.plot(column='w_moto_involved_std', cmap='plasma', scheme='naturalbreaks', edgecolor='white',
           linewidth=0., alpha=0.75, legend=True, ax=ax)

ax.set_axis_off()
ax.set_title('Motorcycles involved in crashes in Medellin 2016-2019 - Standardize Spatial Lag ')

ctx.add_basemap(ax, crs=ne_sa.crs, source=ctx.providers.Stamen.TonerLite)

scale = ScaleBar(dx, 'm', location="lower left", scale_loc="top", length_fraction=0.25)

plt.gca().add_artist(scale)

plt.show()


#Export the tables regarding spatial lag and other attributes

sl_aver_veh.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/sl_aver_veh.xlsx")

sl_bici_involved.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/sl_bici_involved.xlsx")

sl_moto_involved.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/sl_moto_involved.xlsx")

sl_number_crash.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/sl_number_crash.xlsx")


t_aver_veh.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/aver_veh.xlsx")

t_number_auto.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/number_auto.xlsx")

t_number_bici.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/number_bici.xlsx")

t_number_crash.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/number_crash.xlsx")

t_number_moto.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/number_moto.xlsx")

t_total_length.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/tables/total_length.xlsx")


#Save the neighborhood dataframe 'cause it has all the interesting variables

ne_sa.to_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/ne_sa.geojson", driver='GeoJSON')
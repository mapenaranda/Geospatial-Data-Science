# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 16:16:55 2023

@author: Mario
"""

import pandas as pd
import geopandas as gpd
import osmnx
import matplotlib.pyplot as plt
import contextily as ctx


#Import geoclean1619 data to create the geodataframe and compute the spatial calculations

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/geoclean1619.csv")

df = df[(df['latitude'] > 5.80) & (df['latitude'] < 7.00)]

df = df[(df['longitude'] > -76.00) & (df['longitude'] < -75.40)]

#Turn into geometries considering Coordinate Reference System (CRS)   

geo = gpd.points_from_xy(x = df['longitude'], y = df['latitude'], crs = 'EPSG:4326')

gdf = gpd.GeoDataFrame(df, geometry = geo)

#Now, compute a polygon that covers all the crashes in Medellin

crashes_ch = gdf.unary_union.convex_hull

#Now find amenities using OSM for the polygon computed before

#Other amenities are: college, driving_school, library, training, university, bicyle parking,
#bus_station, car_rental, car_wash, charging_station, fuel, parking, taxi, bank, nightclub

#For other amenities visit https://wiki.openstreetmap.org/wiki/Key:amenity

pois =  osmnx.pois_from_polygon(crashes_ch, amenities = ['restaurant', 'bar'])

#Convert the crs from degrees to meter to measure and count the amount of amenities in a radious of 500m
#around each crash record

gdf_albers = gdf.to_crs(epsg = 3311)
pois_albers = pois.to_crs(epsg = 3311)

#Now, we create the buffer (it creates a polygon around each record)

gdf_albers['buffer_500m'] = gdf_albers.buffer(500)

joined = gpd.sjoin(pois_albers, gdf_albers.set_geometry('buffer_500m')[['filed_id', 'buffer_500m']], op = 'within')

#Count the amenities

poi_count = joined.groupby('filed_id')['name'].count().to_frame('poi_count')

gdf_w_counts = gdf_albers.merge(poi_count, left_on = 'filed_id', right_index = True).fillna({'poi_count': 0})


#Graph the corresponding map

f, ax = plt.subplots(1, figsize = (9, 9))

gdf_w_counts.plot(column = 'poi_count',
                  scheme = 'quantiles',
                  alpha = 0.5,
                  legend = True,
                  ax = ax)

ctx.add_basemap(ax,
                crs = gdf_albers.crs.to_string(),
                source = ctx.providers.Stamen.Toner)
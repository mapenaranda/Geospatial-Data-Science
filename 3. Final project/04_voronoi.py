# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 15:57:49 2023

@author: Mario
"""

import geopandas as gpd
import pandas as pd
import osmnx as ox

pluv = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/voronoi_pluv.geojson")

rain = gpd.read_file("C:/Users/Mario/Desktop/PluviometrosDiarioGEO.geojson")

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/final_file_gds.csv")

#Get the polygon of medellin to clip with pluv

limit = ox.geocode_to_gdf('Medellin, Colombia')

pluv_med = gpd.clip(pluv, limit, keep_geom_type=True)

#Give geometry to the crashes

df = df[df['latitude'] >= limit['bbox_south'].iloc[0]]
df = df[df['latitude'] <= limit['bbox_north'].iloc[0]]

df = df[df['longitude'] <= limit['bbox_east'].iloc[0]]
df = df[df['longitude'] >= limit['bbox_west'].iloc[0]]

geo = gpd.points_from_xy(x=df['longitude'], y=df['latitude'], crs='EPSG:4326')

gdf = gpd.GeoDataFrame(df, geometry=geo)

#Filter rain database

rain = rain[(rain['fecha'] >= '2016-01-01') & (rain['fecha'] < '2020-01-01')]

rain = rain[['codigo', 'fecha', 'P1', 'P2', 'Latitude', 'Longitude', 'geometry']]

rain['precipitation'] = rain[['P1', 'P2']].max(axis=1)


#Compute a spatial join to store the attributes

precip = pluv_med.sjoin(rain, how='inner')

precip.drop(labels=['index_right'], axis=1, inplace=True)


#Join dataframe to get the precipitation spatiallly and temporally

final = gdf.sjoin(precip, how='left', predicate='intersects').loc[lambda d: d['date _dmy'].eq(d['fecha'])]

final.to_csv("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/date_and_time.csv")
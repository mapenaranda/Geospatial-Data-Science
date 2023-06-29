# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 18:47:45 2023

@author: Mario
"""

import geopandas as gpd
import pandas as pd
import numpy as np


red = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/red_med.gpkg")

ne = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/barrios.geojson")

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/final_file_gds.csv")

#Compute the area of the neighborhoods

ne = ne.to_crs('EPSG:3857')

ne['area'] = ne.area

red = red.to_crs('EPSG:3857')

#Filter the database of the network

red = red[['ShapeSTAre', 'bridge', 'change_dir',
           'code', 'fclass', 'length(m)', 'maxspeed',
           'mod', 'name', 'nod_f', 'nod_i', 'oneway',
           'source', 'target', 'tunnel', 'geometry']]

#Compute a spatial join to get the attribute of the neighborhoods

sjoined = gpd.sjoin(red, ne, how='inner')

road = sjoined.groupby('OBJECTID')['length(m)'].sum()

road.rename('road_length(m)', inplace=True)

#Add the new field to the neighborhood database

ne = ne.join(road, on='OBJECTID', how='left')

#Compute the road density

ne['road_density'] = ne['road_length(m)']/ne['area']

#Save the new neighborhood database for further work

ne.to_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/barrios.geojson", driver='GeoJSON')
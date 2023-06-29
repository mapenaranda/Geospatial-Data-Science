# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:03:43 2023

@author: Mario
"""

import geopandas as gpd
import pandas as pd

routes = gpd.read_file("C:/Users/Mario/Desktop/ciclorrutas.gpkg")

ne = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/ne_sa.geojson")

ne = ne[['OBJECTID', 'CODIGO', 'COMUNA', 'BARRIO', 'NOMBRE_BARRIO', 'SECTOR',
       'NOMBRE_COMUNA', 'SHAPE__Area', 'SHAPE__Length',
       'road_length(m)', 'road_density', 'geometry']]

routes = routes.to_crs("EPSG:3857")

routes['cyc_length(m)'] = routes.length

routes = routes[routes['ESTADO'] == 'Existente']


routes = routes.sjoin(ne)

routes['cyc_density(m/km2)'] = (routes['cyc_length(m)']*1000**2)/routes['SHAPE__Area']


cyclist_infrastructure = routes.groupby(['NOMBRE_COMUNA', 'NOMBRE_BARRIO'])['cyc_length(m)', 'cyc_density(m/km2)'].sum().sort_values(ascending=False, by=['cyc_length(m)'])

total_length = routes['cyc_length(m)'].sum()/1000

cyclist_infrastructure.to_csv("C:/Users/Mario/Desktop/infra.csv")
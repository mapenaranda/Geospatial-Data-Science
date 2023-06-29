# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 11:49:41 2023

@author: Mario
"""

import pandas as pd
import geopandas as gpd
import seaborn as sns

#Read the datasets

ars = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/ars.geojson")

cctv = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/cctv.geojson")

fd = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/ft.geojson")

population = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/population.geojson")

semaf = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/traffic_lights.geojson")

neig = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/ne_sa.geojson")

#Change the coordinates for the database of the neighborhoods

neig = neig.to_crs('EPSG:4326')

#Drop na values

ars = ars.dropna(axis=0)

#Select the columns of interest in each dataframe

ars = ars[['NAME', 'geometry']]

cctv = cctv[['LOCALIZACION', 'geometry']]

fd = fd[['DESCRIPCIO', 'VEL_MAX_K', 'geometry']]

semaf = semaf[['COD_BARRIO', 'geometry']]

neig = neig[['OBJECTID', 'CODIGO', 'COMUNA', 'BARRIO', 'NOMBRE_BARRIO', 'NOMBRE_COMUNA',
            'road_length(m)', 'road_density', 'number_crash', 'aver_veh',
            'bici_involved', 'moto_involved', 'auto_involved', 'geometry']]


merge = neig[['OBJECTID', 'CODIGO', 'COMUNA', 'BARRIO', 'NOMBRE_BARRIO', 'NOMBRE_COMUNA', 'geometry']]

#Compute the spatial joins for all the interesting variables

ars = ars.sjoin(merge, how='inner')

ars.drop(['index_right'], axis=1, inplace=True)


cctv = cctv.sjoin(merge, how='inner')

cctv.drop(['index_right'], axis=1, inplace=True)


fd = fd.sjoin(merge, how='inner')

fd.drop(['index_right'], axis=1, inplace=True)


semaf = semaf.sjoin(merge, how='inner')

semaf.drop(['index_right'], axis=1, inplace=True)

#Compute the attributes using groupby

total_ars = ars.groupby('OBJECTID')['CODIGO'].count()

total_ars.rename('total_ars', inplace=True)


total_cctv = cctv.groupby('OBJECTID')['CODIGO'].count()

total_cctv.rename('total_cctv', inplace=True)


total_fd = fd.groupby('OBJECTID')['CODIGO'].count()

total_fd.rename('total_fd', inplace=True)


total_semaf = semaf.groupby('OBJECTID')['CODIGO'].count()

total_semaf.rename('total_semaf', inplace=True)


#Now. merge the computations with the dataset containing neighborhoods

neig.set_index('OBJECTID', inplace=True)

to_merge = [total_ars, total_cctv, total_fd, total_semaf]

neig = neig.join(to_merge)

neig.fillna(0, inplace=True)

neig['total_dispo'] = neig['total_ars'] + neig['total_cctv'] + neig['total_fd']

#

n = neig[['road_length(m)', 'road_density', 'number_crash', 'aver_veh',
          'total_ars', 'total_cctv', 'total_fd', 'total_semaf', 'total_dispo']]

sns.pairplot(n)

#Save the file into a GeoJSON for further computations

disp = neig[['CODIGO', 'total_ars', 'total_cctv', 'total_fd', 'total_semaf', 'total_dispo']]

disp.to_csv("C:/Users/Mario/Desktop/disp.csv")
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 07:04:03 2023

@author: Mario
"""

from pysal.model import spreg
from pysal.lib import weights
from pysal.explore import esda
from scipy import stats

import statsmodels.formula.api as sm

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

#import the dataframes to contruct the spatial regression

ne_sa = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/ne_sa.geojson")

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/date_and_time.csv")

estrato = pd.read_csv("C:/Users/Mario/Desktop/estrato.csv")

disp = pd.read_csv("C:/Users/Mario/Desktop/disp.csv")

#Clean the neighborhood geodataframe

ne_sa = ne_sa[['OBJECTID', 'CODIGO', 'COMUNA', 'BARRIO', 'NOMBRE_BARRIO',
               'NOMBRE_COMUNA', 'SHAPE__Area', 'SHAPE__Length', 'geometry']]

ne_sa = ne_sa.to_crs('EPSG:4326')

#Merge estrato with neighborhood dataframe

ne_sa['CODIGO'] = ne_sa['CODIGO'].astype('Int64')

ne_sa = ne_sa.merge(estrato, how='left', left_on='CODIGO', right_on='CODIGO_BARRIO')


#Merge dispositives with ne_sa by neighborhood code

ne_sa = ne_sa.merge(disp, how='left', left_on='CODIGO', right_on='CODIGO')


#Convert df into a geodataframe

df = df[['filed_id', 'datetime', 'year', 'month', 'day', 'accident_type', 
         'accident_address', 'longitude', 'latitude', 'number_veh',
         'av_driver_age', 'moto_involved', 'bici_involved', 'auto_involved',
         'damage', 'injured', 'dead', 'precipitation']]

gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df['longitude'], df['latitude'], crs='EPSG:4326'))

#Now, compute a spatial join to get the neighborhood name and social status

gdf = gdf.sjoin(ne_sa, how='left')

gdf = gdf[['filed_id', 'datetime', 'year', 'month', 'day', 'accident_type',
           'accident_address', 'longitude', 'latitude', 'number_veh',
           'av_driver_age', 'moto_involved', 'bici_involved', 'auto_involved',
           'injured', 'precipitation', 'geometry', 'index_right',
           'OBJECTID_x', 'CODIGO', 'COMUNA', 'BARRIO', 'NOMBRE_BARRIO', 'NOMBRE_COMUNA', 'ESTRATO',
           'total_ars', 'total_cctv', 'total_fd', 'total_semaf', 'total_dispo']]

gdf = gdf[gdf['injured'] == 1]

gdf.rename(columns={'OBJECTID_x': 'OBJECTID'}, inplace=True)

#Compute the interesting variables grouped by datetime and beighborhood

crashes = gdf.groupby(['year', 'month', 'day', 'OBJECTID'])['number_veh'].count()

crashes.rename('number_crashes', inplace=True)

vehicles = gdf.groupby(['year', 'month', 'day', 'OBJECTID'])['number_veh'].mean()

vehicles.rename('number_veh', inplace=True)

age = gdf.groupby(['year', 'month', 'day', 'OBJECTID'])['av_driver_age'].mean()

age.rename('driver_age', inplace=True)

moto_involved = gdf.groupby(['year', 'month', 'day', 'OBJECTID'])['moto_involved'].count()

precipitation = gdf.groupby(['year', 'month', 'day', 'OBJECTID'])['precipitation'].max()


#Group by the gdf dataframe for further analysis

gdf = gdf.groupby(['year', 'month', 'day', 'OBJECTID'])['ESTRATO'].max()

#Merge the dataframes to define the model variables

to_join = [crashes, vehicles, age, moto_involved, precipitation]

gdf = gdf.to_frame()

gdf = gdf.join(to_join)

gdf = gdf.merge(ne_sa, how='left', left_on='OBJECTID', right_on='OBJECTID_x')

gdf['status'] = np.where(gdf['ESTRATO_x'] <= 3, 'low', 'high')


################################# SPATIAL REGRESSION ##################################

variable_names = ['ESTRATO_x', 'precipitation',
                  'total_semaf', 'total_dispo']

#'number_veh', 
#'driver_age'
#'total_ars', 'total_cctv', 'total_fd', 


variable_names2 = ['ESTRATO_x', 'number_veh', 'driver_age',
                   'moto_involved', 'precipitation', 'total_ars',
                   'total_cctv', 'total_fd', 'total_semaf', 'total_dispo']

sns.pairplot(gdf[variable_names])

plt.figure(figsize=(12,6))

sns.heatmap(gdf[variable_names2].corr(), vmin=-1, vmax=1, annot=True)

knn = weights.KNN.from_dataframe(gdf, k=5)

################ SPATIAL HETEROGENEITY

#### SPATIAL FIXED-EFFECTS (FE)

m_sfe = spreg.OLS_Regimes(gdf['number_crashes'].values, gdf[variable_names].values,
                          gdf['NOMBRE_BARRIO'].tolist(),
                          constant_regi='many',
                          cols2regi=[False]*len(variable_names),
                          regime_err_sep=True,
                          name_y='number_crashes', name_x=variable_names)

print(m_sfe.summary)

#### SPATIAL REGIMES

m_sr = spreg.OLS_Regimes(gdf['number_crashes'].values, gdf[variable_names].values,
                          gdf['status'].tolist(),
                          constant_regi='many',
                          regime_err_sep=False,
                          name_y='number_crashes', name_x=variable_names)

print(m_sr.summary)




################# SPATIAL DEPENDENCE

### SPATIAL LAGGED EXOGENOUS REGRESSORS (WX)

wx = gdf[variable_names].apply(lambda y: weights.spatial_lag.lag_spatial(knn, y)).rename(columns=lambda c: 'w_'+c)

slx_exog = gdf[variable_names].join(wx)

m_sler = spreg.OLS(gdf[['number_crashes']].values, slx_exog.values,
                  name_y='number_crashes', name_x=slx_exog.columns.tolist())

print(m_sler.summary)


### SPATIAL ERROR MODEL

m_se = spreg.GM_Error_Het(gdf['number_crashes'].values, gdf[variable_names].values,
                          w=knn, name_y='number_crashes', name_x=variable_names)

print(m_se.summary)


### SPATIAL LAG MODEL

m_sl = spreg.GM_Lag(gdf[['number_crashes']].values, gdf[variable_names].values,
                     w=knn, name_y='number_crashes', name_x=variable_names)

print(m_sl.summary)
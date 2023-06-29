# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:06:42 2023

@author: Mario
"""

from esda.moran import Moran

import libpysal.weights.set_operations as Wsets
from libpysal.weights import Queen, KNN
from pysal.lib import weights

from sklearn import cluster
from sklearn.cluster import KMeans, AgglomerativeClustering

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import geopandas as gpd
import contextily as cx
import seaborn as sns

from pysal.lib import weights
from pysal.explore import esda
from pysal.viz import splot
from splot.esda import plot_moran
from splot.esda import plot_local_autocorrelation


#Read the neighborhood dataframe with its attributes

ne_sa = gpd.read_file("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/layers/ne_sa.geojson")

#Create a list with the variables to consider

variables = ['road_length(m)', 'road_density', 'number_crash', 'aver_veh',
       'bici_involved', 'moto_involved', 'auto_involved']

w = Queen.from_dataframe(ne_sa)

#Compute Moran's I for each variable

result = [Moran(ne_sa[var], w) for var in variables]

#Display on table

moran = pd.DataFrame([(var, res.I, res.p_sim) for var, res in zip(variables, result)],
                     columns=['Variable', "Moran's I", "p-value"]).set_index('Variable')

#Compute local autocorrelation indexes    

lisa_road_density = esda.Moran_Local(ne_sa['road_density'], w)

lisa_number_crash = esda.Moran_Local(ne_sa['number_crash'], w)

lisa_aver_veh = esda.Moran_Local(ne_sa['aver_veh'], w)

lisa_bici_involved = esda.Moran_Local(ne_sa['bici_involved'], w)

lisa_moto_involved = esda.Moran_Local(ne_sa['moto_involved'], w)

lisa_auto_involved = esda.Moran_Local(ne_sa['auto_involved'], w)

#Plot local autocorralation

plot_local_autocorrelation(lisa_road_density, ne_sa, 'road_density')

plot_local_autocorrelation(lisa_number_crash, ne_sa, 'number_crash')

plot_local_autocorrelation(lisa_aver_veh, ne_sa, 'aver_veh')

plot_local_autocorrelation(lisa_bici_involved, ne_sa, 'bici_involved')

plot_local_autocorrelation(lisa_moto_involved, ne_sa, 'moto_involved')

plot_local_autocorrelation(lisa_auto_involved, ne_sa, 'auto_involved')
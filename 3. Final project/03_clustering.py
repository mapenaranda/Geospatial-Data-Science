# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:53:27 2023

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


################################ K-MEANS #####################################

n_clus = 6

kmeans = cluster.KMeans(n_clusters=n_clus)

kcls = kmeans.fit(ne_sa[variables])

ne_sa['kcls'] = kcls.labels_

#Plot the clusters obtained before

f, ax = plt.subplots()

ne_sa.plot(column='kcls', categorical=True, legend=True, linewidth=0, ax=ax, cmap='Blues')

ax.set_axis_off()

plt.title("Medellin's Crashes Classification using KMeans, K=" + str(n_clus))

plt.show()


#Gain deeper insights by computing the barplot and the average values of the clusters

ksizes = ne_sa.groupby('kcls').size()

ksizes.plot.bar()


kmeans_sum = ne_sa.groupby('kcls')[variables].mean()

kmeans_sum = kmeans_sum.T


#Construct clusters profiles

tidy_ne = ne_sa.set_index('kcls')

tidy_ne = tidy_ne[variables]

tidy_ne = tidy_ne.stack()

tidy_ne = tidy_ne.to_frame()

tidy_ne.reset_index(inplace=True)

tidy_ne = tidy_ne.rename(columns={'level_1': 'attribute', 0: 'values'})



facets = sns.FacetGrid(data=tidy_ne, col='attribute', hue='kcls', sharey=False, sharex=False, aspect=2, col_wrap=3)

facets.map(sns.kdeplot, 'values', fill=True).add_legend()


#Compute the regionalization

w = weights.Queen.from_dataframe(ne_sa)

n_clus2 = 16

sagg = cluster.AgglomerativeClustering(n_clusters=n_clus2, connectivity=w.sparse)

sagg_cls = sagg.fit(ne_sa[variables])

ne_sa['sagg'] = sagg_cls.labels_


f, ax = plt.subplots()

ne_sa.plot(column='sagg', categorical=True, legend=True, linewidth=0, ax=ax, cmap='viridis')

ax.set_axis_off()

plt.title("Crashes regions in Medellin K=" + str(n_clus2))

plt.show()

moran.to_csv("C:/Users/Mario/Desktop/moran.csv")
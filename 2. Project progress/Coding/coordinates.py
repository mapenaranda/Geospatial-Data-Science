# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 15:28:23 2023

@author: Mario
"""

import pandas as pd
import numpy as np

coor16 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates_16.xlsx")

coor17 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates_17.xlsx")

coor18 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates_18.xlsx")

#Rename columns of interest

col_dic = {'RADICADO': 'filed_id',
           'X_MAGNAMED': 'x_magnamed', 'Y_MAGNAMED':'y_magnamed',
           'LONGITUD': 'longitude', 'LATITUD': 'latitude'}

coor16.rename(columns = col_dic, inplace = True)

coor17.rename(columns = col_dic, inplace = True)

coor18.rename(columns = col_dic, inplace = True)

#Columns to keep

coor16 = coor16[['filed_id', 'longitude', 'latitude']]

coor17 = coor17[['filed_id', 'longitude', 'latitude']]

coor18 = coor18[['filed_id', 'longitude', 'latitude']]

#Drop repeated columns based on filed_id

coor16 = coor16.drop_duplicates(subset = ['filed_id'])

coor17 = coor17.drop_duplicates(subset = ['filed_id'])

coor18 = coor18.drop_duplicates(subset = ['filed_id'])

#Set filed_id as an integrer

coor16['filed_id'] = coor16['filed_id'].astype(int)

coor17['filed_id'] = coor17['filed_id'].astype(int)

coor18['filed_id'] = coor18['filed_id'].astype(int)


#Now, we are going to organize the coordinates for 2019

coor19_1 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates_19.xlsx")

coor19_2 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates2_19.xlsx")

coor19_3 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates3_19.xlsx")

#Next step is to append al files related to coordinates for 2019

coor19_a = pd.concat([coor19_1, coor19_2, coor19_3])

#Drop rows with duplicated values in coor19

coor19_a = coor19_a.drop_duplicates(subset = ['filed_id'])

#We want to drop rows that contain na values to merge this file latter with no_missing files

coor19_a = coor19_a.dropna()

#Upload missing file in order to merge then and complete the coordinates for 2019

miss19_1 = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/no_missing.csv")

miss19_2 = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/no_missing2.csv")

miss19_3 = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/no_missing3.csv")

#Merge all no_missing files

no_miss19 = pd.concat([miss19_1, miss19_2, miss19_3])

no_miss19 = no_miss19.drop(labels = ['Unnamed: 0.2', 'Unnamed: 0.1', 'index'], axis = 1)

#Merge coor19 with no_miss19 to fulfil the coordinates regarding 2019

coor19 = pd.concat([coor19_a, no_miss19])

#Columns to keep

coor19 = coor19[['filed_id', 'latitude', 'longitude']]

#Rearrange column order

coor19 = coor19[['filed_id', 'longitude', 'latitude']]

#Finally appen coo16, coor17, coor18 and coor19 dataframes to consolidate a file called coordinates

coordinates1619 = pd.concat([coor16, coor17, coor18, coor19])

coordinates1619.reset_index()

coordinates1619.to_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates1619.csv")



#Create file with outliers to review

outliers = coordinates1619[coordinates1619['latitude'] >= 7]

verif = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Crashes/clean_1619.xlsx")

verif = verif[['filed_id', 'accident_address', 'zone', 'city', 'area']]

#Merge outliers with verif to review the address structure

out = outliers.merge(right = verif, how = 'left', left_on = 'filed_id', right_on = 'filed_id')
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 18:55:17 2023

@author: Mario
"""

import pandas as pd
import numpy as np

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/clean1619.csv")

#Create a dataframe to review the accuracy of the coordinates. This most consider latitudes with values
#greater than 7 or lower than 5 and longitudes with values greater than -74 and lower than -76

df1 = df.query('latitude > 7.00')
df2 = df.query('latitude < 5.00')
df3 = df.query('longitude < -76')
df4 = df.query('longitude > -74')

#Select new dataframe 2019 (year) and 'Unknown' (zones) for geocoding

df5 = df.query("zone == 'Unknown'")

df5 = df5[df5['year'] == 2019]

#Do the same for 2019 (year) and 'Otras Entidades' (zones)

df6 = df.query("zone == 'Otras Entidades'")

df6 = df6[df6['year'] == 2019]

#Concatenate these dataframes to generate the final database with the coordinates to review

review = pd.concat([df1, df2, df3, df4, df5, df6])

#Drop repeated addressess

review = review.drop_duplicates(subset = ['filed_id'])

#Drop unnecessary columns

review = review[['filed_id', 'record', 'accident_address',
                 'city','area', 'longitude', 'latitude']]

#Clear the addresses to facilitate the geocoder

review['accident_address'] = review['accident_address'].astype('string')

str1 = {'Carrera 333 Calle 999': 'Carrera 33 Calle 99', 'Carrera 999 Calle 999': 'Carrera 99',
        'Calle 999 Carrera 999': 'Calle9', 'Desconocida 5 Carrera 384': 'Calle 5 Carrera 38',
        'Carrera 85 Cc Norte Calle 76 Norte': 'Carrera 85 C', 'Carrera 201 Calle 210': 'Carrera 20 Calle 21'}

review = review.replace({'accident_address': str1})

#Delete values in longitude and latitude columns

review['latitude'].loc[:] = np.nan

review['longitude'].loc[:] = np.nan

#Save the file to geocode again the coordinates

review.to_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/Coordinates/coor_review.csv")
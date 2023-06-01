# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 19:04:43 2023

@author: Mario
"""

import pandas as pd
import numpy as np

#Now, we are going to organize the coordinates for 2019

coor19_1 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates_19.xlsx")

coor19_2 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates2_19.xlsx")

coor19_3 = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates3_19.xlsx")

#Next step is to append al files related to coordinates for 2019

coor19 = pd.concat([coor19_1, coor19_2, coor19_3])

#Drop rows with duplicated values in coor19

coor19 = coor19.drop_duplicates(subset = ['filed_id'])

#Left the missing values from the dataframe

coor19 = coor19[coor19['latitude'].isna()]

coor19 = coor19.reset_index()

#Remove string 'Con' to improve the accuracy of the geocoder

coor19['accident_address'] = coor19['accident_address'].astype('string')

coor19['accident_address'] = coor19['accident_address'].str.replace('Con ', '')

#Split dataframes to facilitate the computations

missing = coor19.iloc[:10548]

missing2 = coor19.iloc[10549 : 21096]
                       
missing3 = coor19.iloc[21097 : 31644]

missing.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/missing.xlsx")

missing2.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/missing2.xlsx")

missing3.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/missing3.xlsx")
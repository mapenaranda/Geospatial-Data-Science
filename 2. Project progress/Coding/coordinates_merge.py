# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 15:03:53 2023

@author: Mario
"""
import pandas as pd
import numpy as np

#Upload reviewed coordinate's file

reviewed = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coor_reviewed.csv")

reviewed = reviewed[['filed_id', 'longitude', 'latitude']]

#Upload clean1619 to replace the wrong coordinates

clean1619 = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/clean1619.csv")

#Add correct values to the clean1619 file

clean1619 = clean1619.merge(reviewed, how = 'left', left_on = 'filed_id', right_on = 'filed_id')

#Replace values

conditions = [clean1619['longitude_x'] < -75.8, clean1619['longitude_x'] > -74.5]

conditions2 = [clean1619['latitude_x'] < 5, clean1619['latitude_x'] > 7]



choices = [clean1619['longitude_y'], clean1619['longitude_y']]

choices2 = [clean1619['latitude_y'], clean1619['latitude_y']]



clean1619['longitude'] = np.select(conditions, choices, clean1619['longitude_x'])

clean1619['latitude'] = np.select(conditions2, choices2, clean1619['latitude_x'])

#Keep columns of interest

clean1619 = clean1619[['filed_id', 'record', 'year', 'month', 'day', 'date _dmy',
                       'hour', 'only_hour', 'only_minutes', 'minute_interval', 'hour_30min',
                       'accident_type', 'accident_severity', 'vehicle_type', 'service_type',
                       'vehicle_brand', 'vehicle_year', 'accident_address', 'zone', 'city',
                       'area', 'type_of_facility', 'driver_age', 'driver_gender',
                       'longitude', 'latitude']]

clean1619 = clean1619.dropna(subset = ['longitude', 'latitude'])

clean1619.to_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/geoclean1619.csv")
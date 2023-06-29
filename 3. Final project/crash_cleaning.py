# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 13:05:55 2023

@author: Mario
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import datetime


df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/geoclean1619.csv")

pluv = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Climate variables/pluviometers.xlsx")

#Replace the age of 825 within driver_age column



#Replace records that are similar to motorcycles

rep = {'Moped': 'Motorcycle', 'Large_Pick_Up_Truck': 'Pick_Up', 'Articulated_Bus': 'Bus'}

df = df.replace({'vehicle_type': rep})

#Now, create new binary columns considering the involvement of vulnerable road users

df['moto_involved'] = np.where(df['vehicle_type'] == 'Motorcycle', 1, 0)

df['bici_involved'] = np.where(df['vehicle_type'] == 'Bicycle', 1, 0)

df['auto_involved'] = np.where(df['vehicle_type'] == 'Automobile', 1, 0)

df['bus_involved'] = np.where(df['vehicle_type'] == 'Bus', 1, 0)

df['pickup_involved'] = np.where(df['vehicle_type'] == 'Pick_Up', 1, 0)

df['suv_involved'] = np.where(df['vehicle_type'] == 'Suv', 1, 0)

df['atv_involved'] = np.where(df['vehicle_type'] == 'Atv', 1, 0)

df['cuatri_involved'] = np.where(df['vehicle_type'] == 'Quadricycle', 1, 0)

#Do the same considering the injury between the crashes

df['damage'] = np.where(df['accident_severity'] == 'Property_Damage', 1, 0)

df['injured'] = np.where(df['accident_severity'] == 'Injured', 1, 0)

df['dead'] = np.where(df['accident_severity'] == 'Dead', 1, 0)


#Let's create the new variables to consider in the analysis
#First, consider the total number of vehicles involved in the crashes

no_veh = df.groupby('filed_id')['year'].count()

no_veh.rename('number_veh', inplace=True)

#Second, consider the average age of the drivers involved

av_age = df.groupby('filed_id')['driver_age'].mean()

av_age.rename('av_driver_age', inplace=True)

#Third, consider if the crash record involves a vulnerable user

moto_in = df.groupby('filed_id')['moto_involved'].max()

bici_in = df.groupby('filed_id')['bici_involved'].max()

auto_in = df.groupby('filed_id')['auto_involved'].max()

bus_in = df.groupby('filed_id')['bus_involved'].max()

pickup_in = df.groupby('filed_id')['pickup_involved'].max()

suv_in = df.groupby('filed_id')['suv_involved'].max()

atv_in = df.groupby('filed_id')['atv_involved'].max()

cuatri_in = df.groupby('filed_id')['cuatri_involved'].max()


#Group by considering the severity

damage = df.groupby('filed_id')['damage'].max()

injured = df.groupby('filed_id')['injured'].max()

dead = df.groupby('filed_id')['dead'].max()

#Set filed_id as the index to

df = df.drop_duplicates(subset=['filed_id'])

#Create DateTime column to filter by hour

df['datetime'] = pd.to_datetime(df['date _dmy'] + " " + df['hour'])

df = df.set_index('datetime').between_time('5:30', '18:30').reset_index()

#Get and filter the typical days of the week

df['week_day'] = df['datetime'].dt.day_name()

df['week_day'] = df['week_day'].astype('string')

df = df[(df['week_day'] != 'Monday') &
        (df['week_day'] != 'Friday') &
        (df['week_day'] != 'Saturday') &
        (df['week_day'] != 'Sunday')]

#Compute series with additional information

moto_df = df[df['vehicle_type'] == 'Motorcycle']

auto_df = df[df['vehicle_type'] == 'Automobile']

suv_df = df[df['vehicle_type'] == 'Suv']


moto_brand = moto_df.groupby('vehicle_brand')['moto_involved'].count().sort_values(ascending=False).head(10)

moto_brand.rename('crashes', inplace=True)

auto_brand = auto_df.groupby('vehicle_brand')['auto_involved'].count().sort_values(ascending=False).head(10)

auto_brand.rename('crashes', inplace=True)

suv_brand = suv_df.groupby('vehicle_brand')['suv_involved'].count().sort_values(ascending=False).head(10)

suv_brand.rename('crashes', inplace=True)

#df.set_index('filed_id')





#Drop some columns to complete the merge with the computations

col = ['datetime', 'filed_id', 'year', 'month', 'day',
       'date _dmy', 'hour', 'only_hour', 'only_minutes', 'minute_interval',
       'hour_30min', 'accident_type', 'accident_address',
       'longitude', 'latitude', 'week_day']

df = df[col]

#Merge the dataframe with the series computed above

df.set_index('filed_id', inplace=True)

to_mer = [no_veh, av_age,
          moto_in, bici_in, auto_in, bus_in, pickup_in, suv_in, atv_in, cuatri_in,
          damage, injured, dead]

for i in to_mer:
    df = df.merge(i, how='left', left_index=True, right_index=True)

#Filter the dataset to work only with crashes that resulted in injured people

df = df[df['injured'] == 1]

#Filter the dataset to consider crashes that involved motorcycles, bycicles, and automobiles

df = df[(df['moto_involved'] == 1) |
        (df['bici_involved'] == 1) |
        (df['auto_involved'] == 1)]

#Upload and work with the pluviometer's database

pluv.columns = pluv.columns.str.lower()

pluv = pluv[pluv['ciudad'] == 'Medellin']

pluv = pluv[pluv['corregimiento'].isnull()]

pluv.dropna(subset=['comuna'], inplace=True)

pluv.drop_duplicates(subset=['longitud','latitud'], inplace=True)

pluv = pluv[pluv['longitud'] != 0]

com = {'4 Aranjuez': '04 Aranjuez'}

pluv = pluv.replace({'comuna': com})

pluv['longitude'] = pluv['longitud']/100000

pluv['latitude'] = pluv['latitud']/100000

pluv.drop(labels=['longitud', 'latitud', 'barrio', 'corregimiento', 'vereda'], axis=1, inplace=True)


#Save the current dataframe to continue the analysis

df.to_csv("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/final_file_gds.csv")

#Save the pluviometer dataframe for further analysis

pluv.to_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Climate variables/pluviometer_clean.csv")

#Save the series regarding the brand of the main vehicles

moto_brand.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/moto_brand.xlsx")

auto_brand.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/auto_brand.xlsx")

suv_brand.to_excel("C:/Users/Mario/Documents/UN/02. Master's Program/2023 - 1S/01. Geoespatial Data Science/Assignments/3. Final project/suv_brand.xlsx")
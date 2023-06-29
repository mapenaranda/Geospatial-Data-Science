# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 10:24:23 2023

@author: Mario
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/geoclean1619.csv")

to_drop = ['record', 'Unnamed: 0', 'month', 'day',
           'vehicle_type', 'service_type', 'vehicle_brand',
           'vehicle_year', 'city', 'area']

df.drop(labels=to_drop, axis=1, inplace=True)

df.drop_duplicates(subset=['filed_id'], inplace=True)

df.set_index('filed_id', inplace=True)

df['datetime'] = pd.to_datetime(df['date _dmy'] + " " + df['hour'])

df['month_n'] = df['datetime'].dt.month_name()

df['day_n'] = df['datetime'].dt.day_name()

df['month'] = pd.DatetimeIndex(df['datetime']).month

df['day'] = pd.DatetimeIndex(df['datetime']).weekday

#Change data types to facilitate the computations

df['year'] = df['year'].astype('string')

#Compute year histograms

#Crashes per year

crash_year = sns.histplot(data=df, x='year', shrink=0.5, color='darkblue',
                          stat='count', alpha=0.75).set(title='Crashes per year')

#Crashes per year by type

crash_year_type = sns.histplot(data=df, x='year', hue='accident_type', palette='RdBu',
                               shrink=0.5, multiple='stack',
                               stat='count', alpha=1).set(title='Crashes per type')

#Crashes per month
crash_month = sns.countplot(data=df, x='month', palette='Blues').set(title='Crashes per month')

#Crashes per day
crash_day = sns.countplot(data=df, x='day', palette='YlGnBu').set(title='Crashes per day')

#Crashes per type of facility

crash_facility = sns.histplot(data=df, x='accident_type', hue='type_of_facility', palette='RdBu',
                               shrink=0.5, multiple='stack',
                               stat='count', alpha=1).set(title='Type of crash within the road network')

#Graph pie chart for gender

gender = df.groupby('driver_gender')['year'].count()

gender.rename('crashes', inplace=True)

pie, ax = plt.subplots()

labels = gender.keys()

plt.pie(x=gender, labels=labels,
        autopct='%.1f%%',
        colors=['#6495ED', '#00B2EE', '#1874CD'])

plt.title("Proportion of crashes by gender")


#Graph the timeseries of the crashes per year

mer = []

for i in range(2016, 2020):
           
    hour = df[df['year'] == str(i)].groupby('only_hour')['year'].count()
    
    hour.rename(str(i), inplace=True)
    
    mer.append(hour)
    
hours = pd.DataFrame(index=list(map(lambda x: x, range(0,24))))

for i in mer:
    
    hours = hours.merge(i, left_index=True, right_index=True)

crash_hour = hours.plot.line(color=['#FF7256', '#FF1493', '#C1CDCD', '#104E8B']).set(title='Variation of crashes per hour')

plt.xlabel('hour')
plt.ylabel('crashes')
plt.xticks([0,2,4,6,8,10,12,14,16,18,20,22])
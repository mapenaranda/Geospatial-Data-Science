# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np

#Read database with the crash records

df = pd.read_excel("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Crashes/data_1619.xlsx")

#Strip all spaces within the dataframe

df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

#Capitalize first letter within the dataframe

df = df.applymap(lambda x: x.title() if isinstance(x, str) else x)

#Lowercase column names

df.columns = df.columns.str.lower()

#Convert zone column into string to filter

df['zone'] = df['zone'].astype('string')

#Replace wrong data in zone column of the df

#Important to consider the particular cases of 'Otras entidades' and 'Unknown' in the column zone

#Review values related to 'Las Vegas', 'La Diez', 'La Mota'

zones = {'San Antonio De Prado Jurisdicción': 'Corregimiento 80 – San Antonio de Prado',
         'San Antonio de Prado': 'Corregimiento 80 – San Antonio de Prado',
         'Corregimiento Santa Elena Jurisdicción': 'Corregimiento de 90 – Santa Elena',
         'Corregimiento San Cristobal Jurisdicción': 'Corregimiento 60 – San Cristóbal', 
         'Corregi. Belen Altavista Jurisdicción': 'Corregimiento 70 – Altavista',
         'Alpujarra': 'Comuna 10 - La Candelaria',
         'Laureles': 'Comuna 11 - Laureles - Estadio',
         'Centro': 'Comuna 10 - La Candelaria',
         'Termnal Sur': 'Comuna 15 - Guayabal',
         'Terminal Norte': 'Comuna 5 - Castilla',
         'Estadio': 'Comuna 11 - Laureles - Estadio',
         'El Poblado': 'Comuna 14 - El Poblado',
         'Occidente': np.nan,
         'Las Vegas': 'Comuna 14 - El Poblado',
         'La Minorista': 'Comuna 10 - La Candelaria',
         'Norte': 'Comuna 10 - La Candelaria',
         'La Mota': 'Comuna 16 - Belén',
         'La Mota G': 'Comuna 15 - Guayabal',
         'Carretera Al Mar Jurisdicción': 'Corregimiento 60 – San Cristóbal',
         'Oriente': 'Comuna 5 - Castilla',
         'La Mayorista': 'Comuna 1 - Popular',
         'Zona 4': 'Comuna 10 - La Candelaria',
         'Av Regional': 'Comuna 15 - Guayabal',
         'Parque Berrio': 'San Antonio de Prado',
         'Comuna 1': 'Comuna 1 - Popular',
         'Comuna 2': 'Comuna 2 - Santa Cruz',
         'Comuna 3': 'Comuna 3 - Manrique',
         'Comuna 4': 'Comuna 4 - Aranjuez',
         'Comuna 5': 'Comuna 5 - Castilla',
         'Comuna 6': 'Comuna 6 - Doce de octubre',
         'Comuna 7': 'Comuna 7 - Robledo',
         'Comuna 8': 'Comuna 8 - Villa Hermosa',
         'Comuna 9': 'Comuna 9 - Buenos Aires',
         'Comuna 10': 'Comuna 10 - La Candelaria',
         'Comuna 11': 'Comuna 11 - Laureles - Estadio',
         'Comuna 12': 'Comuna 12 - La América',
         'Comuna 13': 'Comuna 13 - San Javier',
         'Comuna 14': 'Comuna 14 - El Poblado',
         'Comuna 15': 'Comuna 15 - Guayabal',
         'Comuna 16': 'Comuna 16 - Belén'}

df = df.replace({'zone': zones})

#Drop crashes in highways

df = df[(df['zone'] != 'Corregimiento de 90 – Santa Elena') & 
        (df['zone'] != 'Corregimiento 80 – San Antonio de Prado') &
        (df['zone'] != 'Corregimiento 60 – San Cristóbal') &
        (df['zone'] != 'Corregimiento Palmitas Jurisdicción') &
        (df['zone'] != 'Corregimiento 70 – Altavista')]

#Fill nan values in city and area columns

values = {'city': 'Medellín', 'area': 'Urban'}

df = df.fillna(value = values)

#Replace values in area to meet OSM requirements

values2 = {'Urban': 'Perímetro Urbano Medellín'}

df = df.replace({'area': values2})

#Drop columns without value for our analysis

no_col = ['police_officer_id', 'cylinder_capacity ', 'other_address', 'notes']

df = df.drop(no_col, axis = 1)

#Replace unknown values with nan in service_type for consistency

values3 = {'Unknown': np.nan}

df = df.replace({'service_type': values3})

#Replace 'Con' in the crash address

df['accident_address'] = df['accident_address'].astype('string')

values4 = {'Con': ''}

df = df.replace({'accident_address': values4}, regex = True)

values5 = {'  ': ' '}

df = df.replace({'accident_address': values5}, regex = True)

#Read the database with the coordinates

df2 = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coordinates1619.csv")

#To keep columns of interest

df2 = df2[['filed_id', 'longitude', 'latitude']]

#Merge the crash records with the coordinates

df3 = df.merge(df2, how = 'left', left_on = 'filed_id', right_on = 'filed_id')

#Save the clean dataframe in an CSV file

df3.to_csv("C:/Users/Mario/Documents/UN/02. Master's Program/clean1619.csv")

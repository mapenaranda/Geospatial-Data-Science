# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:31:23 2023

@author: Mario
"""

import pandas as pd
import requests
import json

#Read accident addressess

df = pd.read_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/Coordinates/coor_review.csv")

df['country'] = 'Colombia'

#API call and get the latitude & longitude values

for i, row in df.iterrows():
    
    apiAddress = str(df.at[i, 'accident_address']) + ',' + str(df.at[i, 'city']) + ',' + str(df.at[i, 'country'])

    parameters = {
        'key': 'sQoJA20kiRRyhsS6nrDYoM9zBKsk3nqj',
        'location': apiAddress}
    
    response = requests.get("https://www.mapquestapi.com/geocoding/v1/address", params = parameters)
    
    data = json.loads(response.text)['results']
    
    lat = data[0]['locations'][0]['latLng']['lat']
    lng = data[0]['locations'][0]['latLng']['lng']
    
    df.at[i, 'latitude'] = lat
    df.at[i, 'longitude'] = lng
    
df.reset_index()
  
#Save the corrected coordinates data to a CSV

df.to_csv("C:/Users/Mario/Documents/UN/02. Master's Program/Database/Geocoded/coor_reviewed.csv")
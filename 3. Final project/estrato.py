# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 09:22:09 2023

@author: Mario
"""

import pandas as pd

estrato = pd.read_csv("C:/Users/Mario/Desktop/estrato_socioeconomico.csv")

estrato = estrato[estrato['COMUNA'] <= 16]

estrato.drop_duplicates(subset=['CODIGO_BARRIO'], inplace=True)

estrato = estrato[['CODIGO_BARRIO', 'ESTRATO']]

estrato.to_csv("C:/Users/Mario/Desktop/estrato.csv")
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 15:15:32 2023

@author: Mario
"""

import pandas as pd
import numpy as np

mapping = dict(df2[['store_code', 'warehouse']].values)
df1['warehouse'] = df1.store.map(mapping)
print(df1)

   id  store address warehouse
0   1    100     xyz      Land
1   2    200     qwe       Sea
2   3    300     asd      Land
3   4    400     zxc      Land
4   5    500     bnm       Sea

https://stackoverflow.com/questions/46049658/mapping-columns-from-one-dataframe-to-another-to-create-a-new-column
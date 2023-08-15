'''
Copyright (C) University of Chicago - All Rights Reserved

accessors.py defines a number of subroutines that are helpful
for accessing latitude and longitude attributes in dataframes.
This is a crucial step for representing it as a geopandas 
dataframe.

* Major Update Log
09/06/2022 - Main Architecture Designed 
'''
import pandas as pd

def access_by_attribute(long, lat):
	'''Accesses the data by the provided latitude and longitude
	'''
	return lambda df: (df[long],df[lat])

def access_by_location_dict(key):
	'''Accesses the data by the provided latitude and longitude
	'''
	return lambda df: (df[key].apply(pd.Series)['longitude'],\
					   df[key].apply(pd.Series)['latitude'])
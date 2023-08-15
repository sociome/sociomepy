'''
Copyright (C) University of Chicago - All Rights Reserved

arcgis.py defines some arcgis constants that are useful
for loading arcgis address files.
'''

ARCGIS_ADDRESS_L1 = 'ADDRDELIV'
ARCGIS_CITY = 'Post_Comm'
ARCGIS_STATE = 'State'
ARCGIS_BASIC_ZIP = 'Post_Code'
ARCGIS_STREET_ABRREV = 'LSt_Type'
ARCGIS_STREET_DIR = 'LSt_PreDir'
ARCGIS_LAT = 'Lat'
ARCGIS_LONG = 'Long'

ARCGIS_PROJ = [ARCGIS_LAT, ARCGIS_LONG, ARCGIS_ADDRESS_L1, ARCGIS_CITY, ARCGIS_STATE, ARCGIS_BASIC_ZIP, ARCGIS_STREET_ABRREV, ARCGIS_STREET_DIR]

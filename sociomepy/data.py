'''
Copyright (C) University of Chicago - All Rights Reserved

data.py contains the main data structures for modeling 
socio-enivornmental data in the sociome project. Essentially
this data structure, SociomeDataFrame, is a wrapper around 
GeoPandas DataFrames but does a little more in terms of 
assuming regularity and the nature of the downstream modeling. 
It also adds useful logging and geocoding functionality.

* Major Update Log
09/02/2022 - Main Architecture Designed 
'''

#we import just some basic packages
import logging
import datetime
import pandas as pd
import geopandas as gpd


class SociomeDataFrame(object):
	'''SociomeDataFrame is a geospatial dataframe that is designed
	to work with the sociome project. We define our own wrapper data
	structure here because there is a lot of project-specific 
	functionality that we need such as logging, data provenance, and
	handling specific data formats.
	'''

	#defines some global schema definitions
	PRIMARY_SUBDIVISION = 'SUBD'
	LOCATIONS_KEY = 'LOCATIONS'
	CLASS_LOG_PREFIX = '[SociomeDataFrame] '


	#constructors modify the code here to add new types of data sources
	def __init__(self):
		'''Constructs an empty SociomeDataFrame.
		'''
		self.data = pd.DataFrame([]) #initialize data to an empty data frame
		self.subdivisions = []


	@classmethod
	def from_save_file(cls, filename, nrows=-1):
		'''Creates a SociomeDataFrame from a previous saved sociome file

			Parameters:
                    filename (str): A file name (or a file pointer)
                    nrows (int): number of rows to read, -1 means read the whole file
                    
            Returns:
                    sociome (SociomeDataFrame): A SociomeDataFrame with the data
		'''

		timer = datetime.datetime.now()

		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Loading Sociome Object From = ' + filename)

		sociome = cls()

		if nrows == -1:
			sociome.data = gpd.read_file(filename)
		else:
			sociome.data = gpd.read_file(filename, rows=nrows)

		elapsed = (datetime.datetime.now() - timer).total_seconds()
		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + ' from_save_file took' + str(elapsed) + ' s')

		return sociome


	@classmethod
	def from_json(cls, url, accessor):
		'''Creates a SociomeDataFrame from a json url

			Parameters:
                    filename (url): A json file name or url
                    accessor (func): A function that retrieves a lat and long
                    
            Returns:
                    sociome (SociomeDataFrame): A SociomeDataFrame with the data
		'''
		timer = datetime.datetime.now()
		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Loading Sociome Object From JSON File = ' + url)

		sociome = cls()
		df = pd.read_json(url)
		sociome.data = gpd.GeoDataFrame(df, \
									    geometry=gpd.points_from_xy(*accessor(df)))

		#only keep non-empty geometries
		sociome.data = sociome.data[~(sociome.data['geometry'].is_empty | sociome.data['geometry'].isna())]

		sociome.data[SociomeDataFrame.LOCATIONS_KEY] = 1

		elapsed = (datetime.datetime.now() - timer).total_seconds()
		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + ' from_json took ' + str(elapsed) + ' s')

		return sociome


	@classmethod
	def from_arcgis_file(cls, filename, nrows=-1):
		'''Creates a SociomeDataFrame from an arcgis file

			Parameters:
                    filename (str): A file name (or a file pointer)
                    nrows (int): number of rows to read, -1 means read the whole file
                    
            Returns:
                    sociome (SociomeDataFrame): A SociomeDataFrame with the data
		'''

		timer = datetime.datetime.now()
		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Loading Sociome Object From ARCGIS File = ' + filename)

		#import constants from arcgis
		import sociomepy.arcgis as arcgis

		#initialize
		sociome = cls()

		#load
		if nrows == -1:
			df = pd.read_csv(filename)
		else:
			df = pd.read_csv(filename, nrows=nrows)

		#clean
		df[arcgis.ARCGIS_LAT] = df[arcgis.ARCGIS_LAT].where(df[arcgis.ARCGIS_LAT].abs() <= 90)
		df[arcgis.ARCGIS_LONG] = df[arcgis.ARCGIS_LONG].where(df[arcgis.ARCGIS_LONG].abs() <= 90)
		df = df.dropna(subset=[arcgis.ARCGIS_LAT, arcgis.ARCGIS_LONG])

		sociome.data = gpd.GeoDataFrame(df[arcgis.ARCGIS_PROJ], \
									    geometry=gpd.points_from_xy(df[arcgis.ARCGIS_LONG], \
																    df[arcgis.ARCGIS_LAT]))

		#only keep non-empty geometries
		sociome.data = sociome.data[~(sociome.data['geometry'].is_empty | sociome.data['geometry'].isna())]

		sociome.data.set_crs(epsg=4269, inplace=True)
		sociome.data[SociomeDataFrame.LOCATIONS_KEY] = 1

		sociome.subdivisions.append(arcgis.ARCGIS_BASIC_ZIP)

		elapsed = (datetime.datetime.now() - timer).total_seconds()
		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + ' from_arcgis_file took ' + str(elapsed) + ' s')

		return sociome


	'''Code here basic accessor and setting methods
	'''
	def getGeometry(self):
		'''Generates an indexed dataframe by geometry

			Returns:
                sociome (SociomeDataFrame): A SociomeDataFrame with only the geometry
		'''
		return self.data[['geometry']]

	def merge_on_geometry(self, gdf, columns):
		'''Adds data from a GeoDataFrame with the same geometry as the SociomeDataFrame.
		Note: the augmenting data must be in the same order as the original data.

			Returns:
                sociome (SociomeDataFrame): A SociomeDataFrame Updated
		'''

		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Augmenting Data: ' + str(columns))

		gdf = gdf[list(columns.keys())]#keep only the relevant ones
		gdf = gdf.rename(columns=columns)

		self.data = pd.concat([self.data, gdf], axis=1)
		return self



	'''Syntax to make this play nice with geopandas
	'''

	def __getitem__(self, key):	
		s = SociomeDataFrame()
		s.data = self.data[key]
		return s

  
	def __setitem__(self, key, newvalue):
		raise ValueError('Not implemented: semantics unclear')





	'''Code below handles subdividing the data
	'''

	def add_subdivision(self, gdf, subdivision_name, subdivision_key):
		'''Adds a subdivision to the SociomeDataFrame

			Parameters:
					gdf (GeoDataFrame/SociomeDataFrame): A geodata frame with subdivisions
                    subdivision_name (str): The desired name of the subdivision
                    subdivision_name (str): A key identifying the subdivision from the gdf
                    
            Returns:
                    sociome (SociomeDataFrame): A SociomeDataFrame with the data
		'''

		#Simple type conversion
		if isinstance(gdf, SociomeDataFrame):
			gdf = gdf.data 


		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Adding a subdivision ' + str(subdivision_name))

		gdf = gdf[['geometry', subdivision_key]]#keep only the relevant ones
		gdf = gdf.rename(columns={subdivision_key: subdivision_name})

		self.data = gpd.sjoin(self.data, gdf, how='left', op='within')
		self.subdivisions.append(subdivision_name)

		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Complete adding a subdivision ' + str(subdivision_name))

		return self


	def merge_on_subdivision(self, gdf, subdivision, right_on, columns={}):
		'''Associate data indexed by census tract

			Parameters:
					gdf (GeoDataFrame/SociomeDataFrame): A geodata frame with subdivisions
                    subdivision (str): The name of the subdivision in the SociomeDataFrame
                    right_on (str): A key identifying the subdivision from the gdf
                    columns (dict): {right_col => name} A dictionary specifying which columns to link
                    
            Returns:
                    sociome (SociomeDataFrame): A SociomeDataFrame with the data
		'''

		#Simple type conversion
		if isinstance(gdf, SociomeDataFrame):
			gdf = gdf.data 

		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Linking data to subdivision ' + str(subdivision))

		gdf = gdf[[right_on] + list(columns.keys())]#keep only the relevant ones
		gdf = gdf.rename(columns=columns)

		self.data = self.data.merge(gdf, how='left', left_on=subdivision, right_on=right_on)
		return self


	'''Metric Estimation
	'''
	def add_metric_to_data(self, metric, name):
		'''Adds a spatial metric to the given sociomedataframe

			Parameters:
					 metric (SpatialFunction): a metric defined as a spatial function
					 name (str): what to call the metric
  
            Returns:
                    self updated
		'''

		gdf = metric.eval(self) #evaluate the dataframe on the metric
		self.data[name] = gdf['metric']
		return self


	'''Code for serialization
	'''

	def to_file(self, filename):
		'''Saves the data as a file with the specified filename

			Parameters:
					filename (str): A filename to store the data
  
            Returns:
                    None
		'''
		timer = datetime.datetime.now()
		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Saving SociomeDataFrame to File = ' + filename)
		self.data.to_file(filename)

		elapsed = (datetime.datetime.now() - timer).total_seconds()

		logging.info(SociomeDataFrame.CLASS_LOG_PREFIX  + 'Complete Saving SociomeDataFrame took ' + str(elapsed) + 's')


	def to_mpl_file(self, filename, columns, sampling_rate=1):
		'''Visualizes the data as a matplotlib png 

			Parameters:
					filename (str): A filename to store the data
					columns (list[str]): A list of columns to plot
					sampling_rate (optional float): Number 0-1 indicating sampling rate
  
            Returns:
            		None
                    
		'''

		import matplotlib.pyplot as plt

		visualized_metrics = columns

		plots = len(visualized_metrics)

		fig, ax = plt.subplots(1, plots, figsize=(20,10))

		if plots == 1:
			ax = [ax]

		if sampling_rate == 1:
			sample = self.data
		else:
			sample = self.data.sample(frac=sampling_rate)


		for i in range(0, plots):
			
			if visualized_metrics == [SociomeDataFrame.LOCATIONS_KEY]:
				sample.plot(ax=ax[i], column = visualized_metrics[i])
			else:
				sample.plot(ax=ax[i], column = visualized_metrics[i], cmap='OrRd', markersize=1)

			ax[i].set_title(visualized_metrics[i])

		plt.savefig(filename)


	def to_mpl_inline(self, columns, sampling_rate=1):
		'''Visualizes the data inline with matplotlib

			Parameters:
					columns (list[str]): A list of columns to plot
					sampling_rate (optional float): Number 0-1 indicating sampling rate

            Returns:
            		None
                    
		'''

		import matplotlib.pyplot as plt

		visualized_metrics = columns

		plots = len(visualized_metrics)

		fig, ax = plt.subplots(1, plots, figsize=(20,10))

		if plots == 1:
			ax = [ax]

		if sampling_rate == 1:
			sample = self.data
		else:
			sample = self.data.sample(frac=sampling_rate)

		for i in range(0, plots):

			if visualized_metrics == [SociomeDataFrame.LOCATIONS_KEY]:
				sample.plot(ax=ax[i], column = visualized_metrics[i])
			else:
				sample.plot(ax=ax[i], column = visualized_metrics[i], cmap='OrRd', markersize=1)

			ax[i].set_title(visualized_metrics[i])

		plt.show()


	def to_kepler_html(self, filename, columns, sampling_rate=1):
		'''Visualizes the data inline to a kepler html file

			Parameters:
					filename (str): A filename to store the data
					columns (list[str]): A list of columns to plot
					sampling_rate (optional float): Number 0-1 indicating sampling rate

            Returns:
            		None
                    
		'''

		from keplergl import KeplerGl

		#fix
		config = {
		'version': 'v1',
		'config': {
		    'mapState': {
		        'latitude': 41.7418876,
		        'longitude': -87.9063053,
		        'zoom': 10.0
		    }
		}
		}

		if sampling_rate == 1:
			sample = self.data
		else:
			sample = self.data.sample(frac=sampling_rate)

		columns += ['geometry']

		map1=KeplerGl(height=400)
		map1.config = config
		map1.add_data(data=sample[columns])
		map1.save_to_html(file_name=filename)
""" Copyright (C) University of Chicago - All Rights Reserved

metric.py contains all of the primitives for defining sociome metrics.

A metric is a spatial function that estimates a socio-environmental 
metric at a particular latitude an longitude point. For example, one can 
calculate the distance to any park in a city. This is a function over all 
latitude and longitude pairs.

* Major Update Log
09/02/2022 - Main Architecture Designed 
"""
import geopandas as gpd
import pandas as pd
import numpy as np
from geopy import distance

from sklearn.neighbors import BallTree
from rtree import index


class SpatialFunction(object):
	'''A SpatialFunction assigns values to every row in a geopandas dataframe. It 
	defines the main super class for all of the spatial functions.
	'''
	
	def __init__(self, sdf, metric_col = None):
		'''Constructs a SpatialFunction.

		Parameters:
                    sdf (SociomeDataFrame): An input dataframe
                    metric_col (str): A column to construct the function

        Returns:
        			SpatialFunction object
		'''
		self.X = np.array([sdf.data['geometry'].x.to_numpy(), \
						   sdf.data['geometry'].y.to_numpy()]).T
		
		self.N = self.X.shape[0]

		if metric_col is None:
			self.FX = np.zeros(self.N)
		else:
			self.FX = self.gdf[metric_col].to_numpy()

		self.metric_col = metric_col


	def query(self, x):
		'''Return the value at a particular geometry point

		   Parameters: 
		   			   x (numpy array): input lat,long vector

		   Returns:
		   			   scalar value of metric
		'''
		return ValueError("Not Implemented")


	def eval(self, sdf):
		'''Evaluates the function across another SociomeDataFrame

		   Parameters: 
		   			   sdf (SociomeDataFrame): An input dataframe

		   Returns:
		   			   a new dataframe consisting of the evaluation
		'''

		gdf = sdf.data
		pts = np.array([gdf['geometry'].x.to_numpy(), \
						gdf['geometry'].y.to_numpy()]).T

		N = pts.shape[0]
		data = []
		for i in range(N):
			fx = self.query(pts[i,:].reshape(1,-1))
			data.append({'x': pts[i,0], 'y': pts[i,1], 'metric': fx})

		df = pd.DataFrame(data) 
		return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))



#assigns a distance to a certain set of points
class SpatialVoronoiFunction(SpatialFunction):
	'''A spatial voronoi function calculates the distance to the nearest point
	'''
	#a spatial function is a set of points on a map associated with a given value

	def __init__(self, gdf):
		'''Constructs a SpatialVoronoiFunction.

		Parameters:
                    gdf (SociomeDataFrame): An input dataframe
        Returns:
        			SpatialFunction object
		'''
		super(SpatialVoronoiFunction, self).__init__(gdf)
		self.tree = BallTree(self.X)

	def query(self, x):
		#overrides the query function
		_,ind = self.tree.query(x, k=1) 

		ind = ind.flatten()
		return distance.distance(x, self.X[ind,:]).meters



class SpatialDensityFunction(SpatialFunction):
	'''A spatial density function counts the number of items within a radius of a point
	'''

	def __init__(self, gdf, radius=1000):
		'''Constructs a SpatialDensityFunction.

		Parameters:
                    gdf (SociomeDataFrame): An input dataframe
        Returns:
        			SpatialFunction object
		'''
		super(SpatialDensityFunction, self).__init__(gdf)
		self.tree = BallTree(self.X)
		self.bandwidth = radius/111139

	def query(self, x):
		#overrides the query function

		ind = self.tree.query_radius(x, r=self.bandwidth)[0]
		if len(ind) == 0:
			return 0

		return len(ind)



class SpatialSubdivisionFunction(SpatialFunction):
	'''A spatial subdivision function is given two a subdivided data frames and
	extends aggregates within a subdivision to the whole lat/long space.
	'''

	def __init__(self, gdf, subdivision, agg, subdivision_right=None):
		'''Constructs a SpatialSubdivisionFunction.

		Parameters:
                    gdf (SociomeDataFrame): An input dataframe
                    subdivision (str): The name of the subdivision
                    agg (str): The name of the aggregation column
                    subdivision_right (str): The name of the subdivision in the right sdf
        Returns:
        			SpatialFunction object
		'''
		#super(SpatialSubdvisionFunction, self).__init__(gdf, agg)
		
		self.gdf = gdf
		self.agg = agg
		self.subdivision = subdivision

		if subdivision_right is None:
			self.subdivision_right = self.subdivision
		else:
			self.subdivision_right = subdivision_right

	def query(self, x):
		#Do not call this
		raise ValueError("Not Implemented")


	def eval(self, sdf):
		'''Evaluates the function across another SociomeDataFrame

		   Parameters: 
		   			   sdf (SociomeDataFrame): An input dataframe

		   Returns:
		   			   a new dataframe consisting of the evaluation
		'''

		#RHS
		gdf = self.gdf.data #get the dataframe
		gdf = gdf[[self.agg, self.subdivision_right]]#keep only the relevant columns
		gdf = gdf.rename(columns={self.agg: 'metric'})


		gdf_target = sdf.data
		gdf_target = gdf_target.merge(gdf, how='left', left_on=self.subdivision, right_on=self.subdivision_right)
		gdf_target = gdf_target[['metric', 'geometry']]

		return gdf_target



class SpatialIdentityFunction(SpatialFunction):
	'''A spatial identity function simply copies over two dataframes that align on geomtry.
	'''

	def __init__(self, gdf, metric_col):
		'''Constructs a SpatialIdentityFunction.

		Parameters:
                    gdf (SociomeDataFrame): An input dataframe
                    metric_col (str): The metric to copy over
        Returns:
        			SpatialFunction object
		'''
		
		self.gdf = gdf
		self.metric_col = metric_col
		

	def query(self, x):
		#Do not call this
		raise ValueError("Not Implemented")


	def eval(self, sdf):
		'''Evaluates the function across another SociomeDataFrame

		   Parameters: 
		   			   sdf (SociomeDataFrame): An input dataframe

		   Returns:
		   			   a new dataframe consisting of the evaluation
		'''

		#RHS
		gdf = self.gdf.data #get the dataframe
		gdf = gdf.rename(columns={self.metric_col: 'metric'})

		gdf_target = sdf.data
		gdf_target = gdf_target.merge(gdf, how='left', on='geometry')
		gdf_target = gdf_target[['metric', 'geometry']]

		return gdf_target



class SpatialInterpolationFunction(SpatialFunction):
	'''A spatial interpolation function interpolates a continuous function.
	'''

	#takes a geodataframe of point geometry and a metric column
	def __init__(self, gdf, metric_col, sigma2=8e-3, precision=1e-6):
		'''Constructs a SpatialInterpolationFunction.

		Parameters:
                    gdf (SociomeDataFrame): An input dataframe
                    metric_col (str): The metric to interpolate
                    sigma2 (float): The smoothing of the interpolation kernel
                    precision (float): The hard bandwidth of the interpolation kernel
        Returns:
        			SpatialFunction object
		'''

		super(SpatialInterpolationFunction, self).__init__(gdf, metric_col)
		self.tree = BallTree(self.X)
		self.sigma2 = sigma2
		self.bandwidth = -np.log(precision)*sigma2


	def query(self, x):
		#override of the abstract class
		ind = self.tree.query_radius(x, r=self.bandwidth)[0]
		if len(ind) == 0:
			return np.NaN

		norm_list = np.sum(np.power(self.X[ind] - x, 2), axis=1)
		explist = np.exp(-norm_list/self.sigma2)
		return np.dot(explist, self.FX[ind])#/np.sum(explist)





	

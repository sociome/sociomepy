""" Copyright (C) University of Chicago - All Rights Reserved

model.py contains a number of key functions that help us understand
different types of spatial correlations.

* Major Update Log
09/06/2022 - Main Architecture Designed 
"""
import numpy as np
import pandas as pd

from sociomepy.data import SociomeDataFrame

from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler


class GeospatialModel(object):
	'''A geospatial linear model defines a regression model between
	a target variable and a set of explanatory variables. Any sklearn
	model can be used here. By default, we use a ridge regression
	model.
	'''

	def __init__(self, target, explanatory):
		'''Constructs a basic linear model between a target variable
		and a list of explanatory variables.

			Parameters:
					target (str): A target variable
					explanatory (list[str]): A list of possible explanatory variables

            Returns:
            		None

		'''

		#variables
		self.target = [target]
		self.explanatory = explanatory

		#You need a ridge model because there are some highly correlated variables
		self.model = Ridge()



	def clean(self, V):
		'''Removes all missing values from the data.

		Parameters:
			V (nupy array)
		Returns
			V cleaned and standardized
		'''

		col_mean = np.nanmean(V, axis=0)

		#Find indices that you need to replace
		inds = np.where(np.isnan(V))

		#Place column means in the indices. Align the arrays using take
		V[inds] = np.take(col_mean, inds[1])

		return V


	def fit(self, gdf, prediction_name, residual_name):
		'''Fits a model to the provided SociomeDataFrame

			Parameters:
					gdf (SociomeDataFrame): A SociomeDataFrame
            Returns:
            		residual_gdf (SociomeDataFrame): A SociomeDataFrame with 
            		the prediction and residual
		'''

		#Clean and standardize
		X = gdf.data[self.explanatory].to_numpy()
		X = self.clean(X)


		Y = gdf.data[self.target].to_numpy()
		Y = self.clean(Y)

		self.model.fit(X,Y)
		Ypred = self.model.predict(X)

		#sets the stats
		self.set_stats(Ypred, Y, self.model, X)

		gdf = gdf.data.copy()
		gdf[prediction_name] = Ypred
		gdf[residual_name] = Y - Ypred

		s = SociomeDataFrame()
		s.data = gdf[[prediction_name, residual_name, 'geometry']]
		return s



	def set_stats(self, Y, Ypred, model, X):
		'''This function is an internal function that compiles statistics
		about the fit.

		Parameters:
					Y (target)
					Ypred (target)
					model (fit model)
					X (the features)
            Returns:
            		None
		'''
		coefficients = list(zip(self.explanatory, model.coef_[0]))

		self.stats = {'mse': self.mse(Y, Ypred),\
					 'r2': self.r2(Y, Ypred),
					 'coefficients': coefficients}

		effects_list = [{'Variable': var, 'Coefficient': val} for var, val in coefficients]
		self.effects_table = pd.DataFrame(effects_list)
		self.effects_table = self.effects_table.sort_values(by='Coefficient', key=abs)


	#metrics

	#mse
	def mse(self, Y, Ypred):
		return mean_squared_error(Y, Ypred)

	#r2 score
	def r2(self, Y, Ypred):
		return r2_score(Y, Ypred)











class Region(object):
	'''A region is a wrapper around an address file and constructs
	a geospatial dataframe around these addresses.
	'''

	def __init__(self, address_file=None):
		'''Constructor. Pass in an address file in arcgis
		'''

		if not address_file is None:
			#load the data
			logging.info('[SOCIOME] Loading the address file at=' + address_file)
			self.address_file = address_file
			df = pd.read_csv(address_file)

			#clean data
			df = self.clean_lat_long(df)
			self.df = gpd.GeoDataFrame(df[ARCGIS_PROJ], \
									   geometry=gpd.points_from_xy(df[ARCGIS_LONG], \
																   df[ARCGIS_LAT]))

			self.df.set_crs(epsg=4269, inplace=True)
			self.df['locations'] = 1

			logging.info('[SOCIOME] Complete. Loading address file at=' + address_file)


	def clean_lat_long(self, df):
		df[ARCGIS_LAT] = df[ARCGIS_LAT].where(df[ARCGIS_LAT].abs() <= 90)
		df[ARCGIS_LONG] = df[ARCGIS_LONG].where(df[ARCGIS_LONG].abs() <= 90)
		return df.dropna(subset=[ARCGIS_LAT, ARCGIS_LONG])


	def findAddress(self, address, zipcode = None):
		'''Given an address it finds the best match in the dataset

		Returns an index in the data frame as well as a row object
		'''
		timer = datetime.datetime.now()

		subarea = self.df

		if not zipcode is None:
			#filter by zipcode first
			subarea = subarea[subarea['Post_Code'] == float(zipcode)]

		scored_addresses = []
		for i,r in subarea.iterrows():
			address_str = ' '.join([str(r['ADDRDELIV']), str(r['Post_Comm']), str(r['State']), str(int(r['Post_Code'])), str(r['LSt_Type']), str(r['LSt_PreDir'])])
			score = fuzz.token_set_ratio(address_str.lower(), address.lower())
			scored_addresses.append((score, i, r))
		
		scored_addresses.sort()

		elapsed = (datetime.datetime.now() - timer).total_seconds()
		logging.info('[SOCIOME] Address Query Took= ' + str(elapsed) + ' s')

		return scored_addresses[-1][1],scored_addresses[-1][2]


	def getGeometry(self):
		'''Returns an indexed dataframe by geometry
		'''
		return self.df[['geometry']]


	def getFeatureMatrix(self, metrics):
		'''Returns a feature matrix
		'''
		return self.df[metrics].to_numpy()





logging.basicConfig(encoding='utf-8', level=logging.INFO)


gdf = gpd.read_file('../data/acs')
s.add_subdivision(gdf, 'tract', 'GEOID')

#s = SociomeDataFrame.from_arcgis_file('../data/chicago-addresses.csv')
#s.add_subdivision(gdf, 'tract', 'GEOID')
#s.to_file('output.pkl')

s = SociomeDataFrame.from_save_file('output.pkl', nrows=1000)
s.merge_on_subdivision(gdf, 'tract', 'GEOID', {'SE_A1006_2': 'metric'})
s.to_kepler_html('save.html', ['LOCATIONS'])

#print(s.subdivisions)


#s = SociomeDataFrame.from_save_file('output.pkl')

#r = Region('../data/chicago-addresses.csv')
#gdf = gpd.read_file('../data/acs')
#r.associate_contains(gdf, 'GEOID')
#r.to_file('output.pkl')


def augment(self, gdf, as_name):
	pts = np.array([gdf['geometry'].x.to_numpy(), \
						gdf['geometry'].y.to_numpy()]).T
	output = self.to_gdf(pts)
	output[as_name] = output['fx']

	return gdf.merge(output, on='geometry')


#gdf = gpd.read_file('../data/acs')
#print(gdf.columns)
#print(gdf[gdf['GEOID'] == '17031990000'])


#r = Region.from_file('output.pkl')
#r.visualize(['locations'])
#r.associate_merge_tract(gdf, 'GEOID', columns={'SE_A1006_2': 'metric'})

#print(r.head())
#r.visualize(['metric'])


#print(gdf.columns)
#r.associate_contains(gdf, {'GEOID': 'tract'})

#print(r.findAddress("1801 S Michigan", 60616))




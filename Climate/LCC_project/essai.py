class SubDomains( object ):
	'''
	rasterize subdomains shapefile to ALFRESCO AOI of output set
	'''
	def __init__( self, subdomains_fn, rasterio_raster, id_field, name_field, background_value=0, *args, **kwargs ):
		'''
		initializer for the SubDomains object
		The real magic here is that it will use a generator to loop through the 
		unique ID's in the sub_domains raster map generated.
		'''
		import numpy as np
		self.subdomains_fn = subdomains_fn
		self.rasterio_raster = rasterio_raster
		self.id_field = id_field
		self.name_field = name_field
		self.background_value = background_value
		self._rasterize_subdomains( )
		self._get_subdomains_dict( )

	def _rasterize_subdomains( self ):
		'''
		rasterize a subdomains shapefile to the extent and resolution of 
		a template raster file. The two must be in the same reference system 
		or there will be potential issues. 
		returns:
			numpy.ndarray with the shape of the input raster and the shapefile
			polygons burned in with the values of the id_field of the shapefile
		gotchas:
			currently the only supported data type is uint8 and all float values will be
			coerced to integer for this purpose.  Another issue is that if there is a value
			greater than 255, there could be some error-type issues.  This is something that 
			the user needs to know for the time-being and will be fixed in subsequent versions
			of rasterio.  Then I can add the needed changes here.
		'''
		import geopandas as gpd
		import numpy as np

		gdf = gpd.read_file( self.subdomains_fn )
		id_groups = gdf.groupby( self.id_field ) # iterator of tuples (id, gdf slice)

		out_shape = self.rasterio_raster.height, self.rasterio_raster.width
		out_transform = self.rasterio_raster.affine

		arr_list = [ self._rasterize_id( df, value, out_shape, out_transform, background_value=self.background_value ) for value, df in id_groups ]
		self.sub_domains = arr_list
	@staticmethod
	def _rasterize_id( df, value, out_shape, out_transform, background_value=0 ):
		from rasterio.features import rasterize
		geom = df.geometry
		out = rasterize( ( ( g, value ) for g in geom ),
							out_shape=out_shape,
							transform=out_transform,
							fill=background_value )
		return out
	def _get_subdomains_dict( self ):
		import geopandas as gpd
		gdf = gpd.read_file( self.subdomains_fn )
		self.names_dict = dict( zip( gdf[self.id_field], gdf[self.name_field] ) )
def get_mon_year( x ):
	month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-2:]
	return {'month':month, 'year':year, 'fn':x}
def return_means( fn, mask_arr ):
	return np.ma.masked_where( mask_arr == 0, rasterio.open( fn ).read(1) ).mean()

if __name__ == '__main__':
	import rasterio, fiona, glob, os
	import numpy as np
	import pandas as pd
	from pathos import multiprocessing as mp
	import pickle

	shp_fn = '/workspace/Shared/Users/jschroder/LCC/Shp/extent_Prism2.shp'

	Base_path = '/Data/Base_Data/Climate/AK_CAN_2km/projected/AR5_CMIP5_models/'
	Base_path1 = '/Data/Base_Data/Climate/AK_CAN_2km/projected/AR4_CMIP3_models/sresa1b'
	variables = ['pr','tas']
	mod_ar5 = ['MRI-CGCM3','GISS-E2-R' , 'GFDL-CM3', 'CCSM4', 'IPSL-CM5A-LR','CNRM-CM5','MPI-ESM-LR']
	mod_ar4 = ['cccma-cgcm3-1-t47', 'gfdl-cm2-1' , 'miroc3-2-medres' , 'mpi-echam5' , 'ukmo-hadcm3']
	path_list = [os.path.join(Base_path,'rcp85'),os.path.join(Base_path,'rcp45'), Base_path1]
	dic = {}

	for variable in variables :
		print 'Working on %s' %variable
		for p in path_list :
			print 'Working on %s' %p
			if p == Base_path1 :
				models = mod_ar4
			else:
				models = mod_ar5

			for model in models:
				print 'Working on %s' %model
				path = os.path.join(p , model , variable)
				print path

				# list the files in the dir
				l = glob.glob( os.path.join( path, '*.tif' ) )

				# now lets only slice out the filenames we want
				monyear = map( get_mon_year, l )
				df = pd.DataFrame( monyear )
				df = df.sort_values(by=['year', 'month'], ascending=[1, 1])

				l = df.fn.tolist()

				subdomains = SubDomains( shp_fn, rasterio.open(l[0]), 'Id' , 'Name' ).sub_domains
				# subdomains[ subdomains != 1 ] = 0

				pool = mp.Pool( 32 )
				out = pool.map( lambda x: return_means( x, subdomains) , l )
				pool.close()
				pool.join()

				df['mean'] = out
				df['date'] = df['year'].map(str) + '-' + df['month']
				df = df.set_index(pd.to_datetime(df['date']))
				df = df.drop(['year' , 'month' , 'fn', 'date'],1)
				dic['%s-%s'%(model,variable)] = df
		
	tas_month =  [1 , 2 , 3 , 4, 5, 6, 7, 8, 9 , 10 , 11 , 12]
	month_list = ["January" , "February" , "March" , "April" , "May" , "June" , "July" , "August", "September", "October" , "November" , "December"]
	tmp = {}

	# Take the dataframes stored in the dictionnary and grab name of month in order to create value by month table
	for key, value in dic.iteritems():
		for i in tas_month :
			tmp[i] = value[np.in1d(value.index.month,i)]
			df_tmp = pd.DataFrame(index=np.unique(dic[key].index.year))

		for i,j in zip(tas_month,month_list) :
			df_tmp[j] = tmp[i]['mean'].as_matrix()
		
		dic[key] = df_tmp 
		del df_tmp
	del tmp
	#Having issues plotting with Atlas, save the dictionnary as a pickle and use local machine for plotting
	pickle.dump( dic, open( "/workspace/Shared/Users/jschroder/TMP/multimodal_extractionaa.p", "wb" ) )

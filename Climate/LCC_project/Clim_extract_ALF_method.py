#This script use the original class method created by Michael for ALFRESCO post processing and use to extract data from different climate source
# in order to create a plot showing GISS GFDL as well as CRU TS32 historical. It relies on a second script for
#plotting as Atlas can't seem to handlye pyplot


class SubDomains( object ):
	'''
	a class that reads in and prepares a dataset to be used in masking
	'''
	def __init__( self, fiona_shape, rasterio_raster, id_field, **kwargs ):
		'''
		initializer for the SubDomains object

		The real magic here is that it will use a generator to loop through the 
		unique ID's in the sub_domains raster map generated.
		'''
		import numpy as np
		self.sub_domains = self.rasterize_subdomains( fiona_shape, rasterio_raster, id_field, **kwargs )
		self.domains_generator = self._domains_generator() # this may be confusing remove if needed.
		self.sub_domains_path = self._domains_name( fiona_shape, rasterio_raster )
		self.template_raster_path = rasterio_raster.name
	@staticmethod
	def rasterize_subdomains( fiona_shape, rasterio_raster, id_field ):
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
		from rasterio.features import rasterize
		import six
		import numpy as np

		test_shape_field = [ f['properties'][id_field] for f in fiona_shape ][0]
		if fiona_shape:
			if not isinstance( test_shape_field , six.string_types ):
				out = rasterize( ( ( f['geometry'], int(f['properties'][id_field]) ) for f in fiona_shape ),
						out_shape=rasterio_raster.shape,
						transform=rasterio_raster.affine,
						fill=0 )
			elif isinstance( test_shape_field, six.string_types ):
				BaseException ( 'Check the type of the id_field, it can only work with uint8 or vals between 0-255' )
			else:
				BaseException ( 'Check the inputs' )
		elif fiona_shape is None:
			out = rasterio_raster.read_band( 1 )
		else:
			BaseException( 'Check the inputs' )
		return out
	def _domains_name( self, fiona_shape, rasterio_raster, **kwargs ):
		'''
		return a domains shapefile name or None
		'''
		if fiona_shape:
			out_name = fiona_shape.name
		elif fiona_shape is None:
			out_name = rasterio_raster.name
		return out_name
	def _domains_generator( self, **kwargs ):
		'''
		this is a simple generator creator to save on RAM and also so it can be easily regenerated
		for subsequent time steps as it plows through the data.

		NOTE:
			due to pickling issues with both pickle and dill, I had to convert this to a list comprehension
			instead of a generator because generators cannot be pickled using either approach.
		'''
		return [( str( i ), np.ma.masked_where( self.sub_domains != i, self.sub_domains )) for i in np.unique( self.sub_domains ) if i != 0 ]
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

	shp_fn = '/workspace/Shared/Users/jschroder/LCC/Shp/Full_extentbuff.shp'

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

				subdomains = SubDomains( fiona.open(shp_fn), rasterio.open(l[0]), 'Id' ).sub_domains
				subdomains[ subdomains != 1 ] = 0

				pool = mp.Pool( 10 )
				out = pool.map( lambda x: return_means( x, subdomains) , l )
				pool.close

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
	pickle.dump( dic, open( "/workspace/Shared/Users/jschroder/LCC/multimodal_extraction.p", "wb" ) )

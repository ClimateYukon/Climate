#This script as for purpose to extract the average value of CMIP5 and CMIP3 climate models as well as a PRISM baseline
#Results are stored in a dictionnary used in a second step to plot and analyzse those data
class NestedDict(dict):
	'''Used to be able to create keys on the fly while populating the dictionnary'''
	def __missing__(self, key):
		self[key] = NestedDict()
		return self[key]

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
		self.sub_domains = self.rasterize_subdomains( fiona_shape, rasterio_raster, id_field)

	@staticmethod
	def rasterize_subdomains( fiona_shape, rasterio_raster, id_field ):

		from rasterio.features import rasterize
		import six
		import numpy as np

		out = rasterize( ( ( f['geometry'], int(f['properties'][id_field]) ) for f in fiona_shape ),
				out_shape=rasterio_raster.shape,
				transform=rasterio_raster.affine,
				fill=0 )
		return out

def return_means( fn, mask_arr ):
	return np.ma.masked_where( mask_arr == 0, rasterio.open( fn ).read(1) ).mean()

def get_mon_year_modeled( x ):
		month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-2:]
		return {'month':month, 'year':year, 'fn':x}

if __name__ == '__main__':

	import rasterio, fiona, glob, os
	import numpy as np
	import pandas as pd
	from pathos import multiprocessing as mp
	import pickle
	import time
	import itertools
	from collections import defaultdict
	import fiona

	shp = '/workspace/Shared/Users/jschroder/Alec_Alfresco_PP_improvements/Data/Shapefile/Boreal_Tundra_CombinedDomains.shp'
	variables = ['pr','tas']
	CMIP5_models = ['MRI-CGCM3','GISS-E2-R' , 'GFDL-CM3', 'NCAR-CCSM4', 'IPSL-CM5A-LR']
	CMIP4_models =  ['cccma-cgcm3-1-t47' , 'gfdl-cm2-1' , 'miroc3-2-medres' , 'mpi-echam5' , 'ukmo-hadcm3']
	CMIP5_scenario = ['rcp45','rcp60','rcp85']
	CMIP4_scenario = ['sresa1b','sresa2','sresb1']

	base_path = '/Data/Base_Data/Climate/AK_CAN_2km/projected/'
	paths4 = [os.path.join(base_path, 'AR4_CMIP3_models', scenario,model,variable) for model in CMIP4_models for scenario in CMIP4_scenario for variable in variables]
	paths5 = [os.path.join(base_path, 'AR5_CMIP5_models' ,scenario,model,variable) for model in CMIP5_models for scenario in CMIP5_scenario for variable in variables]	
	paths = paths4 + paths5

	dic = NestedDict()
	for path in paths5 :
			print path
			scenario = path.split('/')[-3]
			model = path.split('/')[-2]
			variable = path.split('/')[-1]


			l = glob.glob( os.path.join( path ,'*.tif' ))
			monyear = map( get_mon_year_modeled, l )

				
			df = pd.DataFrame( monyear )
			df = df.sort_values(by=['year', 'month'], ascending=[1, 1])

			l = df.fn.tolist()
			subdomains = SubDomains( fiona.open(shp), rasterio.open(l[0]), 'Id' ).sub_domains
			subdomains[ subdomains != 1 ] = 0

			pool = mp.Pool( 32 )
			out = pool.map( lambda x: return_means( x, subdomains) , l )
			pool.close
			pool.close()
			pool.join()


			df['mean'] = out
			df['date'] = df['year'].map(str) + '-' + df['month']
			df = df.set_index(pd.to_datetime(df['date']))
			df = df.drop(['year' , 'month' , 'fn','date'],1)


			dic[variable][scenario] [model.upper()] = df
	dd=NestedDict
	for variable in dic.iterkeys():
		for scenario in dic[variable].iterkeys():
			list_df = []
			for model in dic[variable][scenario].iterkeys():
				df = dic[variable][scenario][model]
				df.columns = [model]
				list_df.append(df)
			dd[variable][scenario] = pd.concat(list_df , axis=1)


	pickle.dump( dic, open( "/workspace/Shared/Users/jschroder/allmodels5.p", "wb" ) )

def get_mon_year( x ):
	month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-2:]
	return {'month':month, 'year':year, 'fn':x}

def zonal_stats_2(shp , file ,stats='*' , nodata_value = -999) :

	with rasterio.open(file) as src:
		affine = src.affine
		array = src.read(1)
		array[array <= nodata_value] = nodata_value
		meta = src.meta
		meta.update(nodata = nodata_value)
		zs = zonal_stats(shp, array, stats = stats , nodata_value = nodata_value , affine=affine)
	return zs

if __name__ == '__main__':
	import rasterio, fiona, glob, os , itertools , pickle
	import numpy as np
	import pandas as pd
	from pathos import multiprocessing as mp
	from rasterstats import zonal_stats
	from collections import defaultdict

	Base_path = '/Data/Base_Data/Climate/AK_CAN_2km/projected/AR5_CMIP5_models'
	shp = '/workspace/Shared/Users/jschroder/Alec_Alfresco_PP_improvements/Data/Shapefile/Boreal_Tundra_CombinedDomains.shp'
	variables = ('pr','tas')
	models = ['GISS-E2-R', 'GFDL-CM3' , 'IPSL-CM5A-LR' , 'MRI-CGCM3' , 'NCAR-CCSM4' ]
	scenarios = [ 'rcp45' , 'rcp60' , 'rcp85']
	output_path = '/workspace/Shared/Users/jschroder/ALFRESCO_SERDP/Data/'
	CRU_path = '/Data/Base_Data/Climate/AK_CAN_2km/historical/CRU/CRU_TS32/'

	dic = defaultdict( lambda: defaultdict( lambda: defaultdict ) )

	for i in itertools.product([Base_path] , scenarios , models , variables) :

		path = os.path.join(*i)
		l = glob.glob( os.path.join( path, '*.tif' ) )
		monyear = list(map( get_mon_year, l ))
		df = pd.DataFrame( monyear )
		df = df.sort_values(by=['year', 'month'], ascending=[1, 1])

		l = df.fn.tolist()

		pool = mp.Pool( 32 )
		out = pool.map( lambda x: zonal_stats_2( shp, x ,  stats='mean' ) , l )
		pool.close()
		pool.join()

		df['Boreal'] = [ i[0]['mean'] for i in out ]
		df['Tundra'] = [ i[1]['mean'] for i in out ]

		df['date'] = df['year'].map(str) + '-' + df['month']
		df = df.set_index(pd.to_datetime(df['date']))
		df = df.drop(['year' , 'month' , 'fn', 'date'],1)

		dic[ i[3] ][i[2] + "_" + i[1]] =  df 

	for i in itertools.product([CRU_path],variables) :
		path = os.path.join(*i)
		l = glob.glob( os.path.join( path, '*.tif' ) )
		monyear = list(map( get_mon_year, l ))
		df = pd.DataFrame( monyear )
		df = df.sort_values(by=['year', 'month'], ascending=[1, 1])

		l = df.fn.tolist()

		pool = mp.Pool( 32 )
		out = pool.map( lambda x: zonal_stats_2( shp, x ,  stats='mean' ) , l )
		pool.close()
		pool.join()

		df['date'] = df['year'].map(str) + '-' + df['month']
		df = df.set_index(pd.to_datetime(df['date']))
		df = df.drop(['year' , 'month' , 'fn', 'date'],1)

		dic[i[1]]["CRU_TS32"] = df

	dic2 = dict({k : dict(v) for k, v in dic.items() })
	pickle.dump( dic2, open( "/workspace/Shared/Users/jschroder/Climate_full.p", "wb" ) )

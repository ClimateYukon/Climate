def get_mon_year( x ):
	month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[5:]
	return {'month':month, 'year':year, 'fn':x}

def get_year( x ):
	year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-1:]
	return {'year':year[0], 'fn':x}

def return_means( k,list_files) :
	out = [rasterio.open(x).read(1) for x in list_files]

	meta = rasterio.open(list_files[0]).meta
	result = np.mean(out,axis=0,dtype=np.float32)

	month, year = os.path.splitext( os.path.basename( list_files[0] ) )[0].split( '_' )[5:]

	baseline_path = os.path.join( anomalie_path , 'run_avg')

	if not os.path.exists( baseline_path ):
		os.mkdir( baseline_path )
	
	output_filename = os.path.join( baseline_path, 'tas_run_avg%s_C_cru_TS31_%s.tif'%(k,year)) 
	result[result < -1000] = -9999

	meta.update(nodata=-9999)
	with rasterio.open( output_filename, 'w', **meta ) as out:
	  out.write( result, 1 )

	return output_filename
def make_list(df , start , end, month = None):

	if month == None :
		return df.fn[(df.year >= str(start)) & (df.year <= str(end))].tolist()
	else :
		return df.fn[(df.month==str(month)) & (df.year >= str(start)) & (df.year < str (end))].tolist()

if __name__ == '__main__':

	import matplotlib
	matplotlib.use('Agg')
	import rasterio, fiona, glob, os
	import numpy as np
	import itertools
	from functools import partial
	import pandas as pd
	from pathos import multiprocessing as mp
	import matplotlib.pyplot as plt
	import matplotlib.cm as cm
	import pickle
	import time
  	start = 1951
  	end = 2010
	anomalie_path = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/run_avg3_tif'
	if not os.path.exists( anomalie_path ):
		os.mkdir( anomalie_path )
	path_data = '/Data/Base_Data/Climate/AK_800m/historical/singleBand/CRU/cru_TS31/historical/tas'
	#path_data = '/Data/Base_Data/Climate/AK_CAN_2km/historical/singleBand/CRU/cru_TS31/historical/tas'

	l = glob.glob( os.path.join( path_data , '*.tif' ))
	monyear = map( get_mon_year, l )
	df = pd.DataFrame( monyear )
	df = df.sort_values(by=['year', 'month'], ascending=[1, 1])
	
	bounds = np.arange(-3,3.05,0.05)
	ticks = np.arange(-3,4,1)

	print 'done with baseline'
	for k in range(2,11):
		print 'working on runavg %s' %k
		#files = [make_list(df,start,j) for j in range(start + k, end+k ,k)]
		files = [make_list(df,i,j) for i,j in zip(range(start, end, 1),range(start+k , end + k ,1))]
		pool = mp.Pool( 32 )
		func = Partial(return_means,k)
		pool.map( func,files)
		pool.close()
		pool.join()

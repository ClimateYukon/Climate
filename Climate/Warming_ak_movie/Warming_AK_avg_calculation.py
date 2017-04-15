from __future__ import division

def get_mon_year( x ):
	month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[5:]
	return {'month':month, 'year':year, 'fn':x}

def get_year( x ):
	year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-1:]
	return {'year':year[0], 'fn':x}

def return_means( output_path ,bounds, k, method, avg_method, list_files ):
	out = [rasterio.open(x).read(1) for x in list_files]
	year = os.path.splitext( os.path.basename( list_files[-1] ) )[0].split( '_' )[-1:]

	meta = rasterio.open(list_files[0]).meta
	result = np.mean(out,axis=0,dtype=np.float32)

	#UGLY!! But does the job of ignoring the no data value while plotting
	result[result < -1000] = None
	plt.figure(figsize=(20,11.25))

	#http://matplotlib.org/api/pyplot_summary.html?highlight=colormaps#matplotlib.pyplot.colormaps
	plt.axis('off')

   	cmap = cm.RdYlBu_r
 

	norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
	
	output_filename = os.path.join( output_path, '_'.join([ 'CRU_TS31_average',str(year[0]) ]) + '.png' )
	
	plt.figtext(.1,.9,year[0], fontsize=60, ha='left')
	
	img = plt.imshow(result, interpolation='nearest', cmap=cmap, norm=norm)
	plt.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=bounds)
	plt.savefig(output_filename)
	

	# output_filename = os.path.join( output_path, '_'.join([ 'tas_mean_C_cru_TS31',str(year[0]) ]) + '.tif' )
	# result[result < -1000] = -9999

	# meta.update(nodata=-9999)
	# with rasterio.open( output_filename, 'w', **meta ) as out:
	#   out.write( result, 1 )

def make_list(df , start , end):
	return df.fn[(df.year >= str(start)) & (df.year <= str(end))].tolist()

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

	#path = '/Data/Base_Data/Climate/AK_800m/historical/singleBand/CRU/cru_TS31/historical/tas'
  	start = 1951
  	end = 2009
	yearly_data = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/run_avg3_tif/run_avg'

	ref = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/run_avg3_tif/run_avg/tas_run_avg3_C_cru_TS31_1951.tif'
	source = rasterio.open(ref).read(1)
	source[source == -9999] = None
	mean = np.nanmean(source)
	std = np.nanstd(source)

	l = glob.glob( os.path.join( yearly_data , '*.tif' ))
	year = map( get_year, l )
	df = pd.DataFrame( year )
	df = df.sort_values(by=['year'], ascending=1)
	del year
	numbers = [1,2,3,4,5,6,7,8,9,10,15,20,25,30]

	for method,ratio in zip(['1std','1_2std','1_3std' , '1_4std'],[1,1/2,1/3,1/4]) :

		print method
		ref_x = mean - (std*(ratio/2))
		st_bounds = ref_x - (((3/ratio)-1) * (std*ratio))
		bounds = [(st_bounds + (z * ratio * std)) for z in range( 0 , int( (6/ratio)+1 ) )] #for 1

		for k in numbers:
			avg_method = 'avg'
			output_path = '/workspace/Shared/Users/jschroder/TMP/Clim_%s_%syear_%s' %(avg_method , k , method)
			if not os.path.exists( output_path ):
				os.mkdir( output_path )
			print 'working on %s year calculation for average' %k
			files = [make_list(df,i,j) for i,j in zip(range(start, end, k),range(start + k, end + k ,k))]
			
			pool = mp.Pool( 32 )

			#Use partial in order to be able to pass output_path argument to the mapped function
			func = partial( return_means ,output_path ,bounds , k , method , avg_method)
			pool.map( func,files)
			pool.close()
			pool.join()


# video conversion http://ubuntuforums.org/showthread.php?t=2173013

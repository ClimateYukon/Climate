from __future__ import division
def get_mon_year( x ):
	month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[7:]
	return {'month':month, 'year':year, 'fn':x}

def get_year( x ):
	year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-1:]
	return {'year':year[0], 'fn':x}

def return_means(bounds, k, method, list_files ) :
	out = [rasterio.open(x).read(1) for x in list_files]

	meta = rasterio.open(list_files[0]).meta
	result = np.mean(out,axis=0,dtype=np.float32)
	centered_file = len(list_files)/2
	month, year = os.path.splitext( os.path.basename( list_files[int(centered_file)] ) )[0].split( '_' )[7:]
	
	k_path = os.path.join( run_avg_path,'run_avg%s_%s'%(k,method))
	if not os.path.exists( k_path ):
		os.mkdir( k_path )

	tif_path = os.path.join(k_path , 'tif')
	if not os.path.exists( tif_path ):
		os.mkdir( tif_path )

	png_path = os.path.join(k_path , 'png')
	if not os.path.exists( png_path ):
		os.mkdir( png_path )

	output_filename_png = os.path.join( png_path, 'tas_run_avg%s_C_cru_TS32_%s_%s.png'%(k,year,method)) 
	output_filename_tif = os.path.join( tif_path, 'tas_run_avg%s_C_cru_TS32_%s_%s.tif'%(k,year,method)) 




	#UGLY!! But does the job of ignoring the no data value while plotting
	result[result < -1000] = None
	fig =plt.figure(figsize=(20,11.25))
	ax = fig.add_subplot(111)
	#http://matplotlib.org/api/pyplot_summary.html?highlight=colormaps#matplotlib.pyplot.colormaps
	ax.axis('off')


	cmap = cm.RdYlBu_r

	norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

	plt.figtext(.21,0.60,'%s'%(year), fontsize=40, ha='left')
	img = ax.imshow(result, interpolation='nearest', cmap=cmap, norm=norm)
	cbar = fig.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=ticks,orientation='horizontal',fraction=0.070, pad=0.03,shrink=0.6,aspect=30)
	cbar.ax.tick_params(labelsize=20,pad=15) 
	fig.tight_layout()
	
	fig.savefig(output_filename_png)

	
	# result[result < -1000] = -9999
	# with rasterio.open( output_filename_tif, 'w', **meta ) as out:
	# 	out.write( result, 1 )

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
  	end = 2013

  	params = {
	  'figure.subplot.bottom': 0.01,
	  'figure.subplot.left' : 0.01,
	  'figure.subplot.top' : 0.95,
	  'figure.subplot.right': 0.99,
	  }

	run_avg_path = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/centered_running_avg_processed_CRUTS32_official/'
	if not os.path.exists( run_avg_path ):
		os.mkdir( run_avg_path )
	#path_data = '/Data/Base_Data/Climate/AK_CAN_2km/historical/CRU/CRU_TS32/tas'
	path_data = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/TS32_cropped'
	#path_data = '/Data/Base_Data/Climate/AK_CAN_2km/historical/singleBand/CRU/cru_TS31/historical/tas'

	l = glob.glob( os.path.join( path_data , '*.tif' ))
	monyear = map( get_mon_year, l )
	df = pd.DataFrame( monyear )
	df = df.sort_values(by=['year', 'month'], ascending=[1, 1])

 	ref_list = df.fn[df.year == str(start)].tolist()
	ref = [rasterio.open(x).read(1) for x in ref_list]
	ref = np.mean(ref,axis=0,dtype=np.float32)
	ref[ref < -1000] = None
	mean = np.nanmean(ref)
	std = np.nanstd(ref)
	numbers = [3,5,7,9,11,13,15]
	# numbers = [7]
	del ref,ref_list
	# method = '1_2std'
	# ratio = 1/2
	for method,ratio in zip(['1_2std','1_3std' , '1_4std'],[1/2,1/3,1/4]) :


		#for method,ratio in zip(['1_2std'],[1/2]) :

		print method
		ref_x = mean - (std*(ratio/2))
		st_bounds = ref_x - (((3/ratio)-1) * (std*ratio))
		bounds = [(st_bounds + (z * ratio * std)) for z in range( 0 , int( (6/ratio)+1 ) )] 
		#ticks = np.round( bounds , decimals=0 )
		ticks = range(-16,13,2)
		for k in numbers:
			print 'working on runavg%s' %k
			files = [make_list(df,i,j) for i,j in zip(range(start - k//2, end, 1),range(start + k//2, end + k ,1))]
			files = [file for file in files if len(file)>=k*12]

			pool = mp.Pool( 32 )

			#Use partial in order to be able to pass output_path argument to the mapped function
			func = partial( return_means ,bounds , k , method )
			pool.map( func,files)
			pool.close()
			pool.join()

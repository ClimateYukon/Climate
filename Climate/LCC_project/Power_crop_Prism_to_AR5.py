def crop(fl):
	print fl
	out_file = fl.replace('akcan','ak').replace('Uncroped' , 'Croped').replace('/ak83albers','')

	os.system('gdalwarp -cutline %s -crop_to_cutline -dstnodata -9999.0 %s %s'%(shp,fl,out_file))

if __name__ == '__main__':
	import glob
	import os
	from pathos import multiprocessing as mp

	path = '/atlas_scratch/jschroder/LCC/Uncroped_Prism' #copied from /Data/Base_Data/Climate/AK_CAN_2km_v2/PRISM


	shp = '/workspace/Shared/Users/jschroder/LCC/Shp/CMIP5_extent.shp'

	for variable in ['pr','tas']:

		_tmp = os.path.join( path.replace('Uncroped','Croped') , variable )
		if not os.path.exists( _tmp ):
			os.makedirs( _tmp )

		pool = mp.Pool( 32 )
		files = glob.glob(os.path.join(path , variable , 'ak83albers' ,'*.tif'))

		pool.map( crop,files)
		pool.close()
		pool.join()



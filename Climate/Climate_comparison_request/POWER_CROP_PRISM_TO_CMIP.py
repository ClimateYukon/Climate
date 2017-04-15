
import glob
import os
from pathos import multiprocessing as mp

def crop(file):
	out_file = file.replace('historical','AK_historical')
	out_file = os.path.join(out_path , os.path.basename( out_file ))
	os.system('gdalwarp -cutline %s -crop_to_cutline -dstnodata -9999.0 %s %s'%(shp,file,out_file))

path_data = '/workspace/UA/jschroder/TEMP/historical_AkCAN_Prism/tas'

out_path = '/workspace/UA/jschroder/TEMP/historical_AkCAN_Prism_cropped/'
if not os.path.exists( out_path ):
	os.mkdir( out_path )
shp = '/workspace/Shared/Users/jschroder/LCC/Shp/CMIP5_extent.shp'
pool = mp.Pool( 32 )
files = glob.glob(os.path.join(path_data,'*.tif'))
pool.map( crop,files)
pool.close()
pool.join()








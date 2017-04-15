
import glob
import os
from pathos import multiprocessing as mp

def crop(file):
	out_file = file.replace('historical','AK_historical')
	out_file = os.path.join(out_path , os.path.basename( out_file ))
	os.system('gdalwarp -cutline %s -crop_to_cutline -dstnodata -9999.0 %s %s'%(shp,file,out_file))

path_data = '/Data/Base_Data/Climate/AK_CAN_2km/historical/CRU/CRU_TS32/tas'

out_path = '/workspace/Shared/Users/jschroder/AK_warming_movie/Data/TS32_cropped'
if not os.path.exists( out_path ):
	os.mkdir( out_path )
shp = '/Data/Base_Data/GIS/GIS_Data/Vector/Boundaries/Alaska_Albers_ESRI.shp'
pool = mp.Pool( 32 )
files = glob.glob(os.path.join(path_data,'*.tif'))
pool.map( crop,files)
pool.close()
pool.join()








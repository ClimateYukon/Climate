#Draft for single use for the moment. Later this piece of code should be used by other function/loop to be able to plow through
#a list of models and scenario. Another important step would be to figure out how to use multiprocessing. For now it takes 2.5 min
# to go through one folder so one variable one model one scenario.

import rasterio,glob,os
import pandas as pd 
import numpy as np

sub_types = ['season','monthly']
variables = ['pr','tas']
CMIP5_models = ['MRI-CGCM3','GISS-E2-R' , 'GFDL-CM3', 'CCSM4', 'IPSL-CM5A-LR','CNRM-CM5','MPI-ESM-LR']
CMIP4_models =  ['cccma-cgcm3-1-t47' , 'gfdl-cm2-1' , 'miroc3-2-medres' , 'mpi-echam5' , 'ukmo-hadcm3']

start = 2010
end = 2100
steps = 30
periods = range(start,end,steps)

paths = ['/Data/Base_Data/Climate/AK_CAN_2km/projected/AR5_CMIP5_models/rcp45/',
		'/Data/Base_Data/Climate/AK_CAN_2km/projected/AR5_CMIP5_models/rcp85/',
		'/Data/Base_Data/Climate/AK_CAN_2km/projected/AR4_CMIP3_models/sresa2/']


# paths = ['/Data/Base_Data/Climate/AK_CAN_2km/projected/AR4_CMIP3_models/sresa2/']

baseline_input = '/workspace/Shared/Users/jschroder/LCC/wrap/'
output_path = os.path.join(baseline_input,'Deltas')

if not os.path.exists( output_path  ):
	os.mkdir( output_path )

def get_mon_year_historical( x ):
		month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-4:-2]
		return {'month':month, 'year':year, 'fn':x}

def get_mon_year_modeled( x ):
		month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-2:]
		return {'month':month, 'year':year, 'fn':x}

def g_mean(mod_list, base_list, output_filename):
	mod_stack = [ rasterio.open( i ).read_band(1) for i in mod_list]
	mod_stack = np.rollaxis( np.dstack( mod_stack ), axis = -1 )
	mod_avg = np.average( mod_stack, axis = 0 )
	meta = rasterio.open(mod_list.iloc[1]).meta
	mod_avg[mod_avg < -1] = -9999
	meta.update( compress='lzw', crs={ 'init':'EPSG:3338' }, dtype=np.float32, nodata=-9999.0 )
	
	base_stack = [ rasterio.open( i ).read_band(1) for i in base_list]
	base_stack = np.rollaxis( np.dstack( base_stack ), axis = -1 )
	base_avg = np.average( base_stack, axis = 0 )
	meta = rasterio.open(base_list.iloc[0]).meta
	base_avg[base_avg < -1] = -9999
	meta.update( compress='lzw', crs={ 'init':'EPSG:3338' }, dtype=np.float32, nodata=-9999.0 )

	delta = mod_avg - base_avg

	with rasterio.open( output_filename, 'w', **meta ) as out:
		out.write(delta,1)
	print 'Wrote %s to disk ' %(output_filename) 
for sub_type in sub_types:
	for path in paths:
		for variable in variables :

			if path.split('/')[-2] == 'sresa2':
					models = CMIP4_models

			else : models = CMIP5_models

			for model in models :

				l_mod = glob.glob( os.path.join( path,model,variable, '*.tif' ))
				monyear_mod = map( get_mon_year_modeled, l_mod )
				df_mod = pd.DataFrame( monyear_mod )
				df_mod = df_mod.sort(['year', 'month'], ascending=[1, 1])
				df_mod.year = pd.to_numeric(df_mod.year,errors='coerce')
				df_mod.month = pd.to_numeric(df_mod.month,errors='coerce')

				l_base = glob.glob(os.path.join( baseline_input,variable, '*.tif' ))
				monyear_base = map( get_mon_year_historical, l_base )
				df_base = pd.DataFrame( monyear_base )
				df_base = df_base.sort(['year', 'month'], ascending=[1, 1])
				df_base.year = pd.to_numeric(df_base.year,errors='coerce')
				df_base.month = pd.to_numeric(df_base.month,errors='coerce')

				if sub_type == 'season' :
					sub_period_list = [[12,1,2], [3,4,5], [6,7,8], [9,10,11]]
					sub_name_list = ['DJF','MAM','JJA','SON']
				else :
					sub_period_list = [[i] for i in range(1,13)]
					sub_name_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	        
				for start_period in periods :
					end_period = start_period + steps - 1
						
					for sub_period,sub_name in zip(sub_period_list,sub_name_list):
						output_filename =  os.path.join( output_path, '_'.join([ 'Deltas', variable, model ,path.split('/')[-2], sub_name,str(start_period),str(end_period), sub_type,]) + '.tif' )
						if  sub_period == [12 , 1 , 2]:
							#Trying to start with december of the year before the start_period
							tmp_mod = df_mod[(df_mod.year >= start_period - 1) & (df_mod.year <= end_period)]
							#REALLY UGLY, need to find a better way, make sure that 01 and 02 momths are not used for start_period and 12 for end_period
							tmp_mod = tmp_mod[tmp_mod['month'].isin(sub_period)][2:-1]
							print tmp_mod
							tmp_base = df_base[df_base['month'].isin(sub_period)]
							g_mean(tmp_mod.fn,tmp_base.fn,output_filename)

						else :
							
							tmp_mod = df_mod[(df_mod.year >= start_period) & (df_mod.year <= end_period)]

							tmp_mod = tmp_mod[tmp_mod['month'].isin(sub_period)]
							
							tmp_base =df_base[df_base['month'].isin(sub_period)]

							g_mean(tmp_mod.fn,tmp_base.fn,output_filename)


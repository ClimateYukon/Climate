##Draft for single use for the moment. Later this piece of code should be used by other function/loop to be able to plow through
#a list of models and scenario. Another important step would be to figure out how to use multiprocessing. For now it takes 2.5 min
# to go through one folder so one variable one model one scenario.

def create_list(path , hist=False):
	
		l = glob.glob( os.path.join( path, '*.tif' ))
		if len(l) == 0 : print 'empty list with %s'%path
		else : pass
		if hist == False :
			monyear = map( get_mon_year_modeled, l )
		else :
			monyear = map( get_mon_year_historical, l )

		df = pd.DataFrame( monyear )
		df = df.sort_values(['year', 'month'], ascending=[1, 1])
		df.year = pd.to_numeric(df.year,errors='coerce')
		df.month = pd.to_numeric(df.month,errors='coerce')
		return df


def get_mon_year_historical( x ):
		month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-4:-2]
		return {'month':month, 'year':year, 'fn':x}

def get_mon_year_modeled( x ):
		month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-2:]
		return {'month':month, 'year':year, 'fn':x}

def delta_production(list_of_list):
	scenario,model,variable = list_of_list

	df_mod = create_list(os.path.join( path , model , scenario , variable))
	df_base = create_list(os.path.join( baseline_input,variable),hist=True )

	for month , start_period in itertools.product(seasons,periods):

		end_period = start_period + steps - 1

		if  month == [12 , 1 , 2]:
			#Trying to start with december of the year before the start_period
			tmp_mod = df_mod[(df_mod.year >= start_period - 1) & (df_mod.year <= end_period)]
			#REALLY UGLY, need to find a better way, make sure that 01 and 02 momths are not used for start_period and 12 for end_period
			tmp_mod = tmp_mod[tmp_mod['month'].isin(month)][2:-1]
			tmp_mod = [tmp_mod[tmp_mod.month == i].fn for i in month]

			tmp_base = [df_base[df_base.month == i].fn for i in month]
			g_mean(tmp_mod,tmp_base,variable,model,scenario,month,start_period,end_period)
	
		else :
			
			tmp_mod = df_mod[(df_mod.year >= start_period) & (df_mod.year <= end_period)]

			tmp_mod = [tmp_mod[tmp_mod.month == i].fn for i in month]

			tmp_base = [df_base[df_base.month == i].fn for i in month]

			g_mean(tmp_mod,tmp_base,variable,model,scenario,month,start_period,end_period)



def g_mean(mod_list, base_list,variable,model,scenario,month,start_period,end_period):

	meta = rasterio.open(mod_list[0].iloc[0]).meta
	meta.update( compress='lzw', crs={ 'init':'EPSG:3338' }, dtype=np.float32, nodata=-9999.0 )

	mod_stack = np.array([[ rasterio.open( i ).read(1) for i in x] for x in mod_list])
	mod_stack[mod_stack < -1000] = np.nan #Reasonable value for which we can assume everything below will be nodata
	base_stack = np.array([[ rasterio.open( i ).read(1) for i in x] for x in base_list])
	base_stack[base_stack < -1000 ] = np.nan #Reasonable value for which we can assume everything below will be nodata
	mod_avg = np.average( mod_stack, axis = 1 )
	base_avg = np.squeeze( base_stack, axis = 1 ) #goes from (3,1,1186,3218) to (3,1186,3218)
	delta = mod_avg - base_avg
	output_path = os.path.join( output_base, scenario,model,variable )

	if not os.path.exists( output_path  ):
		os.makedirs( output_path )

	for i in range(0,3):
		output_filename =  os.path.join( output_path, '_'.join([ 'Deltas', variable, model ,scenario, str(month[i]),str(start_period),str(end_period),'monthly']) + '.tif' )
		with rasterio.open( output_filename, 'w', **meta ) as out:
			out.write(delta[i],1)

	season = np.average(delta, axis =0)

	output_filename =  os.path.join( output_path, '_'.join([ 'Deltas', variable, model ,scenario, str(month[0]) + '-' + str(month[2]),str(start_period),str(end_period),'seasonal']) + '.tif' )
	with rasterio.open( output_filename, 'w', **meta ) as out:
		out.write(season,1)

if __name__ == '__main__':
	import rasterio,glob,os
	import pandas as pd 
	import numpy as np
	from pathos import multiprocessing as mp
	import itertools

	variables = ['pr','tas']
	CMIP5_models = ['MRI-CGCM3','GISS-E2-R' , 'GFDL-CM3', 'NCAR-CCSM4', 'IPSL-CM5A-LR']
	# CMIP4_models =  ['cccma-cgcm3-1-t47' , 'gfdl-cm2-1' , 'miroc3-2-medres' , 'mpi-echam5' , 'ukmo-hadcm3']
	seasons = [[12,1,2], [3,4,5], [6,7,8], [9,10,11]]
	start = 2010
	end = 2100
	steps = 30
	periods = range(start,end,steps)
	scenarios = ['rcp60','rcp45','rcp85']

	path = '/Data/Base_Data/Climate/AK_CAN_2km_v2/'
	output_base = '/workspace/Shared/Users/jschroder/LCC/Deltas_tiff_v2'
	baseline_input = '/atlas_scratch/jschroder/LCC/Croped_Prism'

	if not os.path.exists( output_base  ):
		os.mkdir( output_base )

	attribute_list = [item for item in itertools.product(scenarios[1:],CMIP5_models,variables)]


	pool = mp.Pool( 32 )

	pool.map( delta_production,attribute_list)
	pool.close()
	pool.join()

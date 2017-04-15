#This script as for purpose to extract the average value of CMIP5 and CMIP3 climate models as well as a PRISM baseline
#Results are stored in a dictionnary used in a second step to plot and analyzse those data


class NestedDict(dict):
	'''Used to be able to create keys on the fly while populating the dictionnary'''
	def __missing__(self, key):
		self[key] = NestedDict()
		return self[key]

def return_means( fn ):
	rst = rasterio.open( fn ).read(1)
	#Had issues with different nodata values, those variables are monthly so no value under -100 are possible
	a = np.ma.masked_where( rst < -100, rst )
	return a.mean()

def get_mon_year_historical( x ):
		month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-4:-2]
		return {'month':month, 'year':year, 'fn':x}

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

	variables = ['pr','tas']
	CMIP5_models = ['MRI-CGCM3','GISS-E2-R' , 'GFDL-CM3', 'CCSM4', 'IPSL-CM5A-LR']
	CMIP4_models =  ['cccma-cgcm3-1-t47' , 'gfdl-cm2-1' , 'miroc3-2-medres' , 'mpi-echam5' , 'ukmo-hadcm3']

	#Trying to deal with all the different input folders at once
	paths = ['/Data/Base_Data/Climate/AK_CAN_2km/projected/AR5_CMIP5_models/rcp45/',
			'/Data/Base_Data/Climate/AK_CAN_2km/projected/AR5_CMIP5_models/rcp85/',
			'/Data/Base_Data/Climate/AK_CAN_2km/projected/AR4_CMIP3_models/sresa2/',
			'/Data/Base_Data/Climate/AK_CAN_2km/historical/singleBand/prism/AK_CAN_2km_PRISM/AK_CAN_geotiffs/',
			]

	dic = NestedDict()

	for path in paths :
		for variable in variables :

			scenario = path.split('/')[-2]
			
			#Trying to navigate the different path which, of course, have different naming conventions
			#Using the ak83albers to differentiate the prism data as the folder structure is different
			if scenario == 'sresa2': models = CMIP4_models
			elif scenario == 'AK_CAN_geotiffs' : models = ['ak83albers']
			else : models = CMIP5_models

			for model in models :
				print model

				if scenario == 'AK_CAN_geotiffs' :
					l = glob.glob( os.path.join( path , variable,model , '*.tif' ))
					monyear = map( get_mon_year_historical, l )
					print l[0]

				else :
					l = glob.glob( os.path.join( path , model , variable, '*.tif' ))
					print l[0]
					monyear = map( get_mon_year_modeled, l )

				
				df = pd.DataFrame( monyear )
				df = df.sort_values(by=['year', 'month'], ascending=[1, 1])

				l = df.fn.tolist()
				#Get ressource not available for cores > 5, will have to troubleshoot that at some point
				pool = mp.Pool( 32 )
				out = pool.map( lambda x: return_means( x) , l )
				pool.close()
				pool.join()


				df['mean'] = out
				df['date'] = df['year'].map(str) + '-' + df['month']
				df = df.set_index(pd.to_datetime(df['date']))
				df = df.drop(['year' , 'month' , 'fn','date'],1)
				
				#Set the right name for observed data and prism as scnenario
				if scenario == 'AK_CAN_geotiffs' :
					dic['Prism']['Observed'][variable] = df

				else : 
					dic[scenario][model.upper()][variable] = df
	#Save as a pickle, not that we will have to reference the class NestedDict() for the pickle to be opened 
	pickle.dump( dic, open( "/workspace/Shared/Users/jschroder/LCC/multimodal_extraction_5models.p", "wb" ) )
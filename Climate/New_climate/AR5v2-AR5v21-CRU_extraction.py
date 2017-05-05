def get_mon_year( x ):
	month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-2:]
	return {'month':month, 'year':year, 'fn':x}

def core( path , feature ):
	print('Computing {}'.format(path))
	import glob
	from rasterstats import zonal_stats
	from pathos import multiprocessing as mp

	l = glob.glob( os.path.join( path, '*.tif' ) )
	monyear = list(map( get_mon_year, l ))
	df = pd.DataFrame( monyear )
	df = df.sort_values(by=['year', 'month'], ascending=[1, 1])
	l = df.fn.tolist()
	pool = mp.Pool( 32 )
	out = pool.map( lambda x: zonal_stats( feature, x ,  stats='mean' ) , l )
	pool.close()
	pool.join()

	df['date'] = df['year'].map(str) + '-' + df['month']
	df = df.set_index(pd.to_datetime(df['date']))
	df = df.drop(['year' , 'month' , 'fn', 'date'],1)
	name = path.split('/')[-3]
	df[name] = [ i[0]['mean'] for i in out ]
	return df

def build_fn(base_path , feature ,variable , model=None , scenario=None ) :

	if model == None and scenario == None :
		path = os.path.join(base_path, variable)
		return core( path, feature)

	else :
		ls = [core(os.path.join(base_path, model, scenario, variable), feature) for model in models]
		return pd.concat(ls,axis=1)

if __name__ == '__main__':
	import fiona, os , pickle
	import pandas as pd

	shp = '/Data/Base_Data/ALFRESCO/ALFRESCO_Master_Dataset/ALFRESCO_Model_Input_Datasets/AK_CAN_Inputs/Extents/ALF-PP_FMO-IEM-LCC_MASTER/single_subregions/UEA-Nowak-AKcrop-Master.shp'
	variables = ('pr','tas')
	models = ['GISS-E2-R', 'GFDL-CM3' , 'IPSL-CM5A-LR' , 'MRI-CGCM3' , 'NCAR-CCSM4' ]
	scenarios = [ 'rcp45' , 'rcp60' , 'rcp85']
	Base_paths = ['/Data/Base_Data/Climate/AK_CAN_2km_v2','/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/downscaled']
	CRU_paths = ['/Data/Base_Data/Climate/AK_CAN_2km_v2/CRU_TS323/historical' , '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/downscaled/ts40/historical']


	lyr = fiona.open(shp)
	ft = [x for x in lyr if x['properties']['Name'] == 'Boreal_AK']

	result = {
		variable : {
			scenario : { 
				Base_path.split("/")[-1] : build_fn(Base_path , ft , variable=variable , model=models , scenario=scenario) 
				for Base_path in Base_paths}
			for scenario in scenarios}
		for variable in variables
		}

	CRU = { 
		 variable : {
			Base_path.split("/")[-2] : build_fn(Base_path , ft , variable ) for Base_path in CRU_paths}
		for variable in variables
		}

	for variable in variables :
		result[variable]['CRU'] = pd.concat(CRU[variable].values(),axis=1)

	pickle.dump( result, open( "/workspace/Shared/Users/jschroder/TMP/Climate_full_allV.p", "wb" ) )

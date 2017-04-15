import glob, os , json, pickle
from alfresco_postprocessing import Calib_plotting as CP

json_path = '/atlas_scratch/jschroder/IEM_2017_boreal/JSON/'
json_list = glob.glob(os.path.join(json_path + '*.json'))
out = '/atlas_scratch/jschroder/IEM_2017_boreal/data'
if not os.path.exists( out ):
	os.makedirs( out )
def extract_name(json) :
	return os.path.basename(json).split('.')[0]

obj = [CP.Scenario(js, os.path.basename(js).split('_')[0], os.path.basename(js).split('_')[1].split('.')[0], js, '#162f3b') for js in json_list]


for domain in obj[0].__dict__['total_area_burned'].keys() :
	dic = {}
	for metric in obj[0].metrics :
		if metric != 'veg_counts':
			data ={ extract_name( ob.caption ): dict(ob.__dict__[metric][domain]) for ob in obj } 
		else :
			data = { extract_name( ob.caption ): dict(ob.__dict__[metric][domain]) for ob in obj if 'Observed' not in ob.caption} 
		
		dic[metric] = data

	output = os.path.join( out, '_'.join([ domain ]) + '.p' )

	pickle.dump( dic, open( output, "wb" ) )


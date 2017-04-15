
from __future__ import division
class NestedDict(dict):
	def __missing__(self, key):
		self[key] = NestedDict()
		return self[key]

if __name__ == '__main__':
	import pandas as pd 
	import os
	import numpy as np
	import matplotlib
	import matplotlib.pyplot as plt
	import matplotlib.lines as mlines
	import seaborn as sns
	import pickle
	import datetime
	from math import pi
	from bokeh.plotting import figure, show, output_file, vplot
	from bokeh.models import HoverTool, BoxSelectTool ,ColumnDataSource

	params = {'axes.labelsize': 20,
		  'axes.titlesize' : 19,
		  'legend.fontsize': 17,
		  'xtick.labelsize':  17,
		  'ytick.labelsize': 17,
		  'figure.subplot.bottom': 0.05,
		  'figure.subplot.left' : 0.05,
		  'figure.subplot.top' : 0.88,
		  'figure.subplot.right': 0.97,
		  'figure.subplot.wspace' : 0.07
		  }

	matplotlib.rcParams.update(params)

	#dic = pickle.load(open("/workspace/Shared/Users/jschroder/LCC/multimodal_extraction_fixed_TBSeos.p", 'rb'))
	#dic = pickle.load(open('/Users/julienschroder/Documents/multimodal_extraction_fixed_TBSeos.p', 'rb'))
	here ='/workspace/Shared/Users/jschroder/LCC/multimodal_extraction_5models.p'
	dic = pickle.load(open(here, 'rb'))
	#dic = pickle.load(open("/home/UA/jschroder/Documents/multimodal_extraction_5models.p", 'rb'))
	output_path = '/workspace/Shared/Users/jschroder/TMP/v4'


	variables = {'pr': 'Precipitation', 'tas' : 'Temperature'}
	if not os.path.exists(output_path):
		os.mkdir(output_path)
	quarters = { 2 : 'FEB' , 5 : 'MAY' , 8 : 'AUG' , 11 : 'NOV'}

	period = [ 2030 , 2040 , 2050 , 2070, 2080 , 2090]
	# period = [ 2030 , 2070, 2080 , 2090]
	
	color1 = ["#8173C5",
	"#9ED54D",
	"#C57830",
	"#CB536C",
	"#6D6D72",
	"#7ED3A5",
	"#69843E",
	"#D0B291",
	"#C855BF",
	"#9BB8D3",
	"#522F4B",
	"#B953C6",
	"#C54D7A",
	"#686FBE",
	"#787A8E"]

	for scenario in dic:
		for model in dic[scenario]:
			for variable in dic[scenario][model]:
				if model == 'Observed' :
					dfo = dic[scenario][model][variable]
					dfo = dfo.resample('Q-FEB').mean().iloc[:-1]
					dic[scenario][model][variable] = dfo

				else :
					dfm = dic[scenario][model][variable]
					dfm = dfm.resample('Q-FEB').mean()
					dfm = dfm[(dfm.index > '2009-12-01')&(dfm.index < '2100-02-01')]
					frames = []
					for k , v in quarters.iteritems():
						tmp = dfm[dfm.index.month == k].resample('10A-%s'%(v)).mean()
						frames.append(tmp)
					dic[scenario][model][variable] = pd.concat(frames).sort_index(axis=0)
					del tmp,frames

	#Compute the deltas, prefered to do it from the dictionnary as we can choose other timespan if wanted without re-extracting
	for scenario in dic:
		for model in dic[scenario]:
			if scenario != 'Observed' : 
				for variable in dic[scenario][model]:
					df = dic[scenario][model][variable]

					obs = dic['Prism']['Observed'][variable]
					frames = []
					for i in obs.index.month :
						tmp = df[df.index.month == i]
						if variable == 'pr':
							tmp.loc[:,'deltas'] =  ((tmp.values - obs[obs.index.month == i]['mean'].values) / obs[obs.index.month == i]['mean'].values )
						elif variable == 'tas' :
							tmp.loc[:,'deltas'] =  tmp.values - obs[obs.index.month == i]['mean'].values
						frames.append(tmp)
					dic[scenario][model][variable] = pd.concat(frames).sort_index(axis=0)
					del df,tmp,frames

			else : pass



	for scenario in dic:
		for model in dic[scenario]:
			for variable in dic[scenario][model] :
				df = dic[scenario][model][variable]
				df.index = ['-'.join(x.split('-')[0:2]) for x in df.index.values.astype('str')]
				del df



	for variable in variables.keys() :
		print variable
		frames = []
		col = []
		for scenario in dic:
			for model in dic[scenario]:
				if model == 'Observed': pass
				else :
					tmp = dic[scenario][model][variable]['deltas']
					frames.append(tmp)
					col.append('%s - %s' %(scenario,model))


		tas_df = pd.concat(frames,axis = 1)
		tas_df.columns = col

		print tas_df
		_tools_to_show = 'box_zoom,pan,save,hover,resize,reset,tap,wheel_zoom'        
		sample = dic['rcp85']['GISS-E2-R'][variable]
		factors = [str(x) for x in sample.index.values]
		p = figure(width=1400, height=900, x_range=factors, tools=_tools_to_show)

		#http://stackoverflow.com/questions/31496628/in-bokeh-how-do-i-add-tooltips-to-a-timeseries-chart-hover-tool	
		#http://comments.gmane.org/gmane.comp.python.bokeh/594
		# FIRST plot ALL lines (This is a hack to get it working, why can't i pass in a dataframe to multi_line?)   
		# It's not pretty but it works. 
		# what I want to do!: p.multi_line(df)
		ts_list_of_list = []
		for i in range(0,len(tas_df.columns)):
			ts_list_of_list.append(tas_df.index.T)

		vals_list_of_list = tas_df.values.T.tolist()

		# Define colors because otherwise multi_line will use blue for all lines...

		p.multi_line(ts_list_of_list, vals_list_of_list, line_color=color1)
		
		# for (colr, leg, x, y ) in zip(color1, col, ts_list_of_list, vals_list_of_list):
		# 	my_plot = p.line(x, y, color= colr, legend= leg)

		# THEN put  scatter one at a time on top of each one to get tool tips (HACK! lines with tooltips not yet supported by Bokeh?) 
		for (name, series) in tas_df.iteritems():
			# need to repmat the name to be same dimension as index
			name_for_display = np.tile(name, [len(tas_df.index),1])

			source = ColumnDataSource({'x': tas_df.index, 'y': series.values, 'series_name': name_for_display})
			# trouble formating x as datestring, so pre-formating and using an extra column. It's not pretty but it works.

			p.scatter('x', 'y', source = source, fill_alpha=0.9, line_alpha=0.3, line_color="black")     

			hover = p.select(dict(type=HoverTool))
			# hover.tooltips = [("Series", "@series_name") ,("Value", "@y"),]
			# hover.mode = 'mouse'

		# p.legend.orientation = "top_left"
		if variable == 'tas' :
			hover.tooltips = [("Series", "@series_name"),("Date", "@x"), ("Value", "@y"),]
			hover.mode = 'mouse'
			p.title = 'Average Deltas Temperature Values by season and decade From PRISM baseline (1961-1990) '
			p.grid.grid_line_alpha=0.3
			p.xaxis.axis_label = 'Average Deltas Temperature Values by season and decade'
			p.yaxis.axis_label = 'Temperature (C)'
		else :
			hover.tooltips = [("Series", "@series_name"), ("Date", "@x"), ("Value", "@y{0.00%}"),]
			hover.mode = 'mouse'
			p.title = 'Average Deltas Precipitation Values by season and decade From PRISM baseline (1961-1990) '
			p.grid.grid_line_alpha=0.3
			p.xaxis.axis_label = 'Average Deltas Precipitation Values by season and decade'
			p.yaxis.axis_label = 'Percentage of change'

		p.xaxis.major_label_orientation = pi/4
		out = os.path.join( output_path,  'Multimodal_deltas_comparison_points_%s.html'%(variable) )
		output_file(out, title="GCM comparison for %s"%(variable))
		show(p)

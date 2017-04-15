
#second is for plotting by 10 years timespan
class NestedDict(dict):
	def __missing__(self, key):
		self[key] = NestedDict()
		return self[key]
from __future__ import division
import pandas as pd 
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns
import pickle
import datetime

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

dic = pickle.load(open("/home/UA/jschroder/Documents/multimodal_extraction_5models.p", 'rb'))
output_path = '/workspace/Shared/Users/jschroder/TMP/'
quarters = { 2 : 'FEB' , 5 : 'MAY' , 8 : 'AUG' , 11 : 'NOV'}

period = [2010 , 2020 , 2030 , 2040 , 2050 , 2060 , 2070, 2080 , 2090]

for scenario in dic:
	for model in dic[scenario]:
		for variable in dic[scenario][model]:
			if model == 'Observed' :
				dfo = dic[scenario][model][variable]
				dfo = dfo.resample('Q-FEB').iloc[:-1]
				dic[scenario][model][variable] = dfo

			else :
				dfm = dic[scenario][model][variable]
				dfm = dfm.resample('Q-FEB')
				dfm = dfm[(dfm.index > '2009-12-01')&(dfm.index < '2100-02-01')]
				frames = []
				for k , v in quarters.iteritems():
					tmp = dfm[dfm.index.month == k].resample('10A-%s'%(v))
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
						tmp.loc[:,'deltas'] =  ((tmp.values - obs[obs.index.month == i]['mean'].values) / obs[obs.index.month == i]['mean'].values ) * 100
					elif variable == 'tas' :
						tmp.loc[:,'deltas'] =  tmp.values - obs[obs.index.month == i]['mean'].values
					frames.append(tmp)
				dic[scenario][model][variable] = pd.concat(frames).sort_index(axis=0)
				del df,tmp,frames

		else : pass

#Getting the plotting ready

#sns.set_palette('deep',19)
sns.set_palette("hls", 10)
#color = sns.color_palette('deep',19)

#from http://tools.medialab.sciences-po.fr/iwanthue/
color1 = ["#8173C5",
"#9ED54D",
"#C57830",
"#CB536C",
"#6D6D72",
"#7ED3A5",
"#69843E",
"#D0B291",
"#C855BF",
"#9BB8D3"]
# #color2 = ["#522F4B",
# "#B953C6",
# "#C54D7A",
# "#686FBE",
# "#787A8E"]

style = {'figure.facecolor': 'white'}
variables = {'pr': 'Precipitation', 'tas' : 'Temperature'}



sns.set(style="whitegrid")
#last piece of reformat, reformat the dictionnary for easier plotting of scenario
sorted_dic = NestedDict()
for scenario in dic:
	if scenario != 'Prism':
		for var in dic['Prism']['Observed']:
			tmp = pd.DataFrame()
			for k , v in dic[scenario].iteritems():
				tmp[k] =  v[var]['deltas']
			sorted_dic[scenario][var] = tmp


for variable in variables:

	for scen in [['rcp85','sresa2'],['rcp45','sresa2']] :

		fig1 = plt.figure()
		figsize = ( 16, 10 )
		ax = fig1.add_subplot(1, 1, 1)
		axes = [ax] + [fig1.add_subplot(1, len(period), l, sharey=ax) for l in range(1, len(period)+1)]

		ax.yaxis.grid(False)
		ax.xaxis.grid(False)

		ax.get_xaxis().set_ticks([])
		for ax in axes[1:]:
			ax.get_yaxis().set_visible(False)
			ax.get_xaxis().set_visible(False)
			ax.set_frame_on(False)
			ax.set_axis_bgcolor('white')

		for j,season in zip(range(1,len(period)+1),period) :
			print season

			mod1 = sorted_dic[scen[0]][variable]
			mod1[mod1.index.year == season].plot(ax=axes[j],color=color1[:5],label= 'CMIP5-%s' %scen[0] ,legend=False,figsize=figsize,lw=1,alpha= 1)

			mod2 = sorted_dic[scen[1]][variable]
			mod2[mod2.index.year == season].plot(ax=axes[j],color=color1[5:],label= 'CMIP5-%s' %scen[1], dashes=[10,2,2,2] ,legend=False,figsize=figsize,lw=1,alpha= 1)

			axes[j].set(title='%s - %s' %(season,season + 9))  


		if variable == 'pr' :
			axes[0].set_ylabel('Percentage of change')
			axes[0].set_xlabel('Average Deltas Precipitation Values by season and decade')
			fig1.suptitle('Average Deltas Precipitation Values by season and decade From PRISM baseline (1961-1990)\n CMIP5 %s Models and CMIP3 %s Models ' %(scen[0],scen[1]),fontsize=18, fontweight='bold')

		else : 	
			axes[0].set_ylabel('Temperature (C)')
			axes[0].set_xlabel('Average Deltas Temperature Values by season and decade')
			fig1.suptitle('Average Deltas Temperature Values by season and decade From PRISM baseline (1961-1990)\n CMIP5 %s Models and CMIP3 %s Models ' %(scen[0],scen[1]),fontsize=18, fontweight='bold')

	
		ax.legend(loc='center left', ncol=2, bbox_to_anchor=(-2.5, 0.1),fontsize = 15, fancybox=True)


		# plt.rcParams.update(params)
		sns.axes_style(style)
		output_filename = os.path.join( output_path, '_'.join([ 'Multimodal_deltas_comparison', variable,str(scen[0]),str(scen[1]) ]) + '.png' )
		print "Writing %s to disk" %output_filename
		sns.despine()
		plt.savefig( output_filename )
		plt.close()





# 		# plt.show()
# 		# plt.close()

# for variable in variables:
	
# 	fig1 = plt.figure()
# 	figsize = ( 16, 10 )
# 	ax = fig1.add_subplot(1, 1, 1)
# 	axes = [ax] + [fig1.add_subplot(1, len(period), l, sharey=ax) for l in range(1, len(period)+1)]

# 	ax.yaxis.grid(False)
# 	ax.xaxis.grid(False)

# 	ax.get_xaxis().set_ticks([])
# 	for ax in axes[1:]:
# 		ax.get_yaxis().set_visible(False)
# 		ax.get_xaxis().set_visible(False)
# 		ax.set_frame_on(False)
# 		ax.set_axis_bgcolor('white')

# 	for scen in [['rcp85','sresa2'],['rcp45','sresa2']] :


# 		for j,season in zip(range(1,len(period)+1),period) :
# 			print season

# 			mod1 = sorted_dic[scen[0]][variable]
# 			mod1[mod1.index.year == season].plot(color=color1[:5],label= 'CMIP5-%s' %scen[0] ,legend=False,figsize=figsize,lw=1,alpha= 1)

# 			mod2 = sorted_dic[scen[1]][variable]
# 			mod2[mod2.index.year == season].plot(color=color1[5:],label= 'CMIP5-%s' %scen[1], dashes=[10,2,2,2] ,legend=False,figsize=figsize,lw=1,alpha= 1)


# 		if variable == 'pr' :
# 			axes[0].set_ylabel('Percentage of change')
# 			axes[0].set_xlabel('Average Deltas Precipitation Values by season and decade')
# 			fig1.suptitle('Average Deltas Precipitation Values by season and decade From PRISM baseline (1961-1990)\n CMIP5 %s Models and CMIP3 %s Models ' %(scen[0],scen[1]),fontsize=18, fontweight='bold')

# 		else : 	
# 			axes[0].set_ylabel('Temperature (C)')
# 			axes[0].set_xlabel('Average Deltas Temperature Values by season and decade')
# 			fig1.suptitle('Average Deltas Temperature Values by season and decade From PRISM baseline (1961-1990)\n CMIP5 %s Models and CMIP3 %s Models ' %(scen[0],scen[1]),fontsize=18, fontweight='bold')

	
# 		ax.legend(loc='center left', ncol=2, bbox_to_anchor=(-2.5, 0.1),fontsize = 15, fancybox=True)


# 		# plt.rcParams.update(params)
# 		sns.axes_style(style)
# 		output_filename = os.path.join( output_path, '_'.join([ 'Multimodal_deltas_comparison', variable,str(scen[0]),str(scen[1]) ]) + '.png' )
# 		print "Writing %s to disk" %output_filename
# 		sns.despine()
# 		plt.savefig( output_filename )
# 		plt.close()





		# plt.show()
		# plt.close()



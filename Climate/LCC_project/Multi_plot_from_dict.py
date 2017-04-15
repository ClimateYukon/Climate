from __future__ import division
class NestedDict(dict):
	def __missing__(self, key):
		self[key] = NestedDict()
		return self[key]

def points_line(variable,scen):
	sns.set_palette(color1)
	style = {'figure.facecolor': 'white'}

	sns.set(style="whitegrid")
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

		mod1 = sorted_dic[scen[0]][variable]
		mod1[mod1.index.year == season].plot(ax=axes[j],style='^',legend=False,figsize=figsize)
		mod1.mean(axis=1).plot(ax=axes[j],color=color2[2],xlim=['%sQ1'%str(season),'%sQ4'%str(season)],figsize=figsize,label='%s Average'%scen[0])

		mod2 = sorted_dic[scen[1]][variable]
		mod2[mod2.index.year == season].plot(ax=axes[j],style='o',legend=False,figsize=figsize)
		mod2.mean(axis=1).plot(ax=axes[j],color=color2[4],xlim=['%sQ1'%str(season),'%sQ4'%str(season)],figsize=figsize,label='%s Average'%scen[1])

		axes[j].set(title='%s - %s' %(season,season + 9))  
		axes[j].set_xlim(['%sQ4'%str(season-1),'%sQ1'%str(season+1)])



	if variable == 'pr' :
		axes[0].set_ylabel('Percentage of change')
		axes[0].set_xlabel('Average Deltas Precipitation Values by season and decade')
		fig1.suptitle('Average Deltas Precipitation Values by season and decade From PRISM baseline (1961-1990)\n CMIP5 %s Models and CMIP3 %s Models ' %(scen[0],scen[1]),fontsize=18, fontweight='bold')

	else : 
		axes[0].set_ylabel('Temperature (C)')
		axes[0].set_xlabel('Average Deltas Temperature Values by season and decade')
		fig1.suptitle('Average Deltas Temperature Values by season and decade From PRISM baseline (1961-1990)\n CMIP5 %s Models and CMIP3 %s Models ' %(scen[0],scen[1]),fontsize=18, fontweight='bold')


	ax.legend(loc='center left', ncol=2, bbox_to_anchor=(-5.3, 0.85),fontsize = 12, fancybox=True)
	# plt.show()

	sns.axes_style(style)
	output_filename = os.path.join( output_path, '_'.join([ 'Multimodal_deltas_comparison_points', variable,str(season),str(scen[0]),str(scen[1]) ]) + '.png' )
	print "Writing %s to disk" %output_filename
	sns.despine()
	plt.savefig( output_filename )
	plt.close()
	del mod1,mod2

def just_lines(variable,scen):

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


	ax.legend(loc='center left', ncol=2, bbox_to_anchor=(-5.3, 0.85),fontsize = 12, fancybox=True)


	# plt.rcParams.update(params)
	sns.axes_style({'figure.facecolor': 'white'})
	output_filename = os.path.join( output_path, '_'.join([ 'Multimodal_deltas_comparison_lines', variable,str(scen[0]),str(scen[1]) ]) + '.png' )
	print "Writing %s to disk" %output_filename
	sns.despine()
	plt.savefig( output_filename )
	plt.close()



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
	color2 = ["#522F4B",
	"#B953C6",
	"#C54D7A",
	"#686FBE",
	"#787A8E"]




	sorted_dic = NestedDict()
	for scenario in dic:
		if scenario != 'Prism':
			for var in dic['Prism']['Observed']:
				tmp = pd.DataFrame()
				for k , v in dic[scenario].iteritems():
					k = k + '_' + scenario
					tmp[k] =  v[var]['deltas']
				sorted_dic[scenario][var] = tmp

	for variable in variables:

		for scen in [['rcp85','sresa2'],['rcp45','sresa2']] :

			points_line(variable,scen)
			just_lines(variable,scen)

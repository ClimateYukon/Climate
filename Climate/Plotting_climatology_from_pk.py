
import pandas as pd 
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import pickle
sns.set_style("whitegrid", {'axes.grid' : False})

output_path = '/workspace/Shared/Users/jschroder/TMP/Climate/'

if not os.path.exists( output_path ):
	os.mkdir( output_path )

dic = pickle.load(open('/workspace/Shared/Users/jschroder/ALFRESCO_SERDP/Data/Climate_files/Dict_CCSM_MRO_historical.p', 'rb'))
sns.set(style="whitegrid")
colors_list = {'tas' : pd.Series(['#d7191c', '#fdae61',  '#2b83ba' ]), 'pr' : pd.Series(['#7b3294', '#008837', '#fc8d59'])}
style = {'figure.facecolor': 'white'}
variable = {'pr': 'Precipitation', 'tas' : 'Temperature'}

filtered_dict = {k:v.ix[2010:2100] for (k,v) in dic.iteritems() if  'CRU' not in k}

for k,v in filtered_dict.iteritems() :
	dic[k] = v

params = {'axes.labelsize': 18,
	'axes.titlesize' : 19,
	'legend.fontsize': 17,
	'xtick.labelsize':  15,
	'ytick.labelsize': 15,
	'figure.figsize': (16, 10),
	'figure.subplot.bottom': 0.07,
	'figure.subplot.left' : 0.07,
	'figure.subplot.top' : 0.83,
	'figure.subplot.right': 0.95,
	'figure.subplot.wspace' : 0.03,
	'figure.facecolor' : 'y',
     }

plt.rcParams.update(params)

for k,value in variable.iteritems() :
	storage = (sns.xkcd_rgb["denim blue"],sns.xkcd_rgb["pale red"])
	colors = [storage[0],storage[1],sns.xkcd_rgb["charcoal"]]

	dic['CRU_TS32-%s'%k] = dic['CRU_TS32-%s'%k].ix[1980:2009]


	fig1 = plt.figure()
	ax = fig1.add_subplot(1, 1, 1)

	ax.yaxis.grid(False)
	ax.set_xlabel('Monthly Values from 2010 to 2100')
	ax.xaxis.grid(False)

	if k == 'pr' :
		ax.set_ylabel('mm')
		months =  [ 5, 6, 7, 8, 9]
		month_list = [ "May","June" , "July" , "August", "September"]
	else :
		ax.set_ylabel('$^\circ$C') 
		months =  [ 3, 4, 5, 6, 7, 8, 9]
		month_list = ["March" , "April" , "May" , "June" , "July" , "August", "September"]

	#Setting ticks to an empty list allows you to use the set label
	ax.get_xaxis().set_ticks([])

	axes = [ax] + [fig1.add_subplot(1, len(months), l, sharey=ax) for l in range(1, len(months)+1)]

	# This piece allows me to keep some labelling on the first plot
	for ax in axes[1:]:
		ax.get_yaxis().set_visible(False)
		ax.get_xaxis().set_visible(False)
		ax.set_frame_on(False)
		ax.set_axis_bgcolor('white')


	#So this is not the main plot, decade points are set up to +4.5 so it looks better,legend are disable for trend lines.
	for j,month in zip(range(1,len(months)+1),month_list):
		axes[j].plot(dic['MRI-CGCM3-%s'%k].index , dic['MRI-CGCM3-%s'%k][month] ,color=colors[0],  lw=0.8,alpha=0.7, label =None )
		axes[j].plot( np.unique(dic['MRI-CGCM3-%s'%k].index[:-1] // 10 * 10) + 4.5 ,dic['MRI-CGCM3-%s'%k][month].groupby(dic['MRI-CGCM3-%s'%k].index // 10 * 10).mean()[:-1], color=colors[0], lw=2.1, label =None)                              
		axes[j].plot(dic['MRI-CGCM3-%s'%k].index, dic['CCSM4-%s'%k][month] ,color=colors[1], lw=0.8,alpha=0.7 , label =None)
		axes[j].plot( np.unique(dic['MRI-CGCM3-%s'%k].index[:-1] // 10 * 10)+4.5 , dic['CCSM4-%s'%k][month].groupby(dic['CCSM4-%s'%k].index // 10 * 10).mean()[:-1], color=colors[1], lw=2.1, label =None)
		axes[j].plot(dic['MRI-CGCM3-%s'%k].index , np.array([dic['CRU_TS32-%s'%k][month].mean()]*len(np.unique(dic['MRI-CGCM3-%s'%k].index))) ,  linestyle= '--' , color=colors[2], lw=1.8, label =None)
		axes[j].set(title=month)   

	#Create label for axis
	# y-axis acreage 
	y1, y2 = ax.get_ylim()
	x1, x2 = ax.get_xlim()

	# make new axis
	ax2 = ax.twinx()

	# Convert celsius and mm to inches and F
	if k == 'pr' :
		pr_conv = 0.0393701
		ax2.set_ylim( y1*pr_conv, y2*pr_conv )
		ax2.set_ylabel( 'Inches' )

	else :
		ax2.set_ylim( (y1*1.8)+32, (y2*1.8)+32 )
		ax2.set_ylabel( '$^\circ$F' )

	ax2.set_xlim( x1, x2 )
	ax2.grid(None)

	# ax2 spines
	ax2.spines[ "top" ].set_visible( False ) 
	ax2.spines[ "left" ].set_visible( False )

	plt.minorticks_on()
	ax.minorticks_on()
	ax2.get_yaxis().get_major_formatter().set_useOffset(False)
	ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	ax2.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

	plt.xlabel( 'Year' )



	#Build the legend
	lMRI = mlines.Line2D([], [], linewidth=2.1, color= colors[0] , label='MRI-CGCM3' )
	lCCSM4 = mlines.Line2D([], [], linewidth=2.1, color=colors[1], label='NCAR-CCSM4' )
	lhistorical = mlines.Line2D([], [],  linestyle= '--',linewidth=1.2, color=colors[2], label='Historical CRU' )

	axes[0].legend(handles = [lMRI,lCCSM4,lhistorical],loc="best",ncol=1, shadow=True, fancybox=True, bbox_to_anchor=[0.2, 1],)  


	output_filename = os.path.join( output_path, '_'.join([ 'Climatology_CCSM4_MRI-CGCM3_historical_', k ,'merged']) + '.png' ) 
	fig1.suptitle('Monthly Average %s \n CMIP5 Models: NCAR-CCSM4 and MRI-CGCM3, RCP 8.5 \n with 1980-2010 Historical CRU Averages' %value,fontsize=18, fontweight='bold')

	plt.savefig( output_filename)

	plt.close()







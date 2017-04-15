import pandas as pd
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from plotly.offline.offline import _plot_html
import numpy as np
import cufflinks as cf
from plotly.graph_objs import *

cf.set_config_file(offline=False, world_readable=True)
import pickle

models = ['cccma_cgcm3_1_sresa1b',
'cccma_cgcm3_1_sresa1b_PreFMO',
'gfdl_cm2_1_sresa1b',
'gfdl_cm2_1_sresa1b_PreFMO',
'miroc3_2_medres_sresa1b',
'miroc3_2_medres_sresa1b_PreFMO',
'mpi_echam5_sresa1b',
'mpi_echam5_sresa1b_PreFMO',
'ukmo_hadcm3_sresa1b',
'ukmo_hadcm3_sresa1b_PreFMO',
'CCSM4_rcp85',
'GFDL-CM3_rcp85',
'GISS-E2-R_rcp85',
'IPSL-CM5A-LR_rcp85',
'MRI-CGCM3_rcp85']

colors = ["#9d63c9","9d63c9",
"#74ba4a","#74ba4a",
"#ca5995","#ca5995",
"#4f8241","#4f8241",
"#d34a3a","#d34a3a",
"#4fba9f",
"#be635e",
"#6587cd",
"#d28b3b",
"#a29443"]

dic = pickle.load(open("/workspace/Shared/Users/jschroder/TMP/Trying.p", 'rb'))
def make_CD(dic):

	def get_veg_ratios( veg_dd ,year_range = (1950,2100), group1=['White Spruce', 'Black Spruce'], group2=['Deciduous'] ):
		'''
		calculate ratios from lists of veg types.
		'''
		begin,end = year_range
		agg1 = sum([ veg_dd[ i ].ix[begin:end] for i in group1 ])
		agg2 = sum([ veg_dd[ i ].ix[begin:end]for i in group2 ])
		return agg1 / agg2



	df = [get_veg_ratios(dic[model]['veg_counts'] )


	 for model in models]
	df_mean = [_df.mean(axis=1) for _df in df ]
	df = pd.concat(df_mean,axis=1)
	df.columns = models


	dash = ['solid','dashdot','solid','dashdot','solid','dashdot','solid','dashdot','solid','dashdot','solid','solid','solid','solid','solid']
	dash = dict(zip(models,dash))
	coldict = dict(zip(models,colors))

	list_data = [Scatter(x=df.index , y = df[model], line = Line(color=coldict[model],width=1.5,dash=dash[model]),name=model,hoverinfo = 'name') for model in models]

	data = Data(list_data)
	layout = Layout(

	    title='Conifer:Deciduous Ratios 1950-2100 , ALFRESCO, AR4 & AR5 models, Boreal Domain',
	    xaxis=dict(title='Year'),
	    yaxis=dict(title='C:D Ratio'),
	    updatemenus=list([
	        dict(
	            x=0.6,
	            y=1.05,
	            yanchor='top',
	            buttons=list([
	                dict(
	                    args=['visible', [True, True, True, True,True, True, True, True,True, True, True, True,True, True, True]],
	                    label='All',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [True, False, True, False,True, False, True, False,True, False, True, True,True, True, True]],
	                    label='PostFMO',
	                    method='restyle'
	                ),                        
	                dict(
	                    args=['visible', [True, True, True, True,True, True, True, True,True, True, False, False,False, False, False]],
	                    label='AR4',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [False, False, False, False,False, False, False, False,False, False, True, True,True, True, True]],
	                    label='AR5',
	                    method='restyle'
	                ),
	                dict(
	                args=['visible', [True, True, False, False,False, False, False, False,False, False, False, False,False, False,False]],
	                    label='cccma_cgcm3_1_sresa1b',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [False, False, True, True,False, False, False, False,False, False, False, False,False, False, False]],
	                    label='gfdl_cm2_1_sresa1b',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [False, False, False, False,True, True, False, False,False, False, False, False,False, False, False]],
	                    label='miroc3_2_medres_sresa1b',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [False, False, False, False,False, False, True, True,False, False, False, False,False, False, False]],
	                    label='mpi_echam5_sresa1b',
	                    method='restyle'
	                ),    
	                dict(
	                    args=['visible', [False, False, False, False,False, False, False, False,True, True, False, False,False, False, False]],
	                    label='ukmo_hadcm3_sresa1b',
	                    method='restyle'
	                ),                         
	            ]),
	        )
	    ]),
	)
	fig = Figure(data=data, layout=layout)

	# That gives me the right figure except I do not have the dropdown menu in my ipython notebook, note that I am experimenting with notebook but the html will be produced outside of a notebook once my code will be ready.


	plot_html, plotdivid, width, height = _plot_html(fig, False, "", True, '100%', 800,"")
	html_start = """
	<html>
	<head>
	  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
	</head>
	<body>"""

	html_end = """
	</body>
	</html>"""

	html_final = html_start + plot_html + html_end
	f = open('/home/UA/jschroder/Desktop/cd_ratio_comp.html', 'w')
	f.write(html_final)
	f.close()

def make_TAB(dic):
	df = pd.concat([dic[model]['total_area_burned'].ix[1950:2100].mean(axis=1).cumsum(axis=0) for model in models],axis=1)
	df.columns = models
	dash = ['solid','dashdot','solid','dashdot','solid','dashdot','solid','dashdot','solid','dashdot','solid','solid','solid','solid','solid']
	dash = dict(zip(models,dash))
	coldict = dict(zip(models,colors))

	list_data = [Scatter(x=df.index , y = df[model], line = Line(color=coldict[model],width=1.5,dash=dash[model]),name=model,hoverinfo = 'name') for model in models]

	data = Data(list_data)
	layout = Layout(

	    title='Cumulative Sum of Annual Area Burned 1950-2100 , ALFRESCO, AR4 & AR5 models, Boreal Domain',
	    xaxis=dict(title='Year'),
	    yaxis=dict(title='Area Burned in km2'),
	    updatemenus=list([
	        dict(
	            x=-0.05,
	            y=1,
	            yanchor='top',
	            buttons=list([
	                dict(
	                    args=['visible', [True, True, True, True,True, True, True, True,True, True, True, True,True, True, True]],
	                    label='All',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [True, False, True, False,True, False, True, False,True, False, True, True,True, True, True]],
	                    label='PostFMO',
	                    method='restyle'
	                ),                        
	                dict(
	                    args=['visible', [True, True, True, True,True, True, True, True,True, True, False, False,False, False, False]],
	                    label='AR4',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [False, False, False, False,False, False, False, False,False, False, True, True,True, True, True]],
	                    label='AR5',
	                    method='restyle'
	                ),
	                dict(
	                args=['visible', [True, True, False, False,False, False, False, False,False, False, False, False,False, False,False]],
	                    label='cccma_cgcm3_1_sresa1b',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [False, False, True, True,False, False, False, False,False, False, False, False,False, False, False]],
	                    label='gfdl_cm2_1_sresa1b',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [False, False, False, False,True, True, False, False,False, False, False, False,False, False, False]],
	                    label='miroc3_2_medres_sresa1b',
	                    method='restyle'
	                ),
	                dict(
	                    args=['visible', [False, False, False, False,False, False, True, True,False, False, False, False,False, False, False]],
	                    label='mpi_echam5_sresa1b',
	                    method='restyle'
	                ),    
	                dict(
	                    args=['visible', [False, False, False, False,False, False, False, False,True, True, False, False,False, False, False]],
	                    label='ukmo_hadcm3_sresa1b',
	                    method='restyle'
	                ),                         
	            ]),
	        )
	    ]),
	)
	fig = Figure(data=data, layout=layout)


	# That gives me the right figure except I do not have the dropdown menu in my ipython notebook, note that I am experimenting with notebook but the html will be produced outside of a notebook once my code will be ready.
	plot_html, plotdivid, width, height = _plot_html(fig, False, "", True, '100%', 800,"")
	html_start = """
	<html>
	<head>
	  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
	</head>
	<body>"""

	html_end = """
	</body>
	</html>"""

	html_final = html_start + plot_html + html_end
	f = open('/home/UA/jschroder/Desktop/TAB.html', 'w')
	f.write(html_final)
	f.close()
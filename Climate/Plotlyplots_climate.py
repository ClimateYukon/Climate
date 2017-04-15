def produce_plot(scen1,scen2,metric):
    dic = pickle.load(open("/workspace/Shared/Users/jschroder/ALFRESCO_SERDP/Comparison_AR4_AR5/Climate_request/allmodelsfinale.p", 'rb'))

    pr = dic[metric]
    for scenario in pr.iterkeys():
        _df = pr[scenario]
        _df.columns = [name + '-' + scenario for name in _df.columns]
        pr[scenario] = _df

    huge = pd.concat([pr[scen1],pr[scen2]], axis=1)
    df=huge
    if metric == 'pr':
        df = df[(df.index.month > 4) & (df.index.month < 10)]
        month_ls = ['May','June','July','August','September']
        month_nb = [5,6,7,8,9]
    else : 
        df = df[(df.index.month > 2) & (df.index.month < 10)]
        month_ls = ['March','April','May','June','July','August','September']
        month_nb = [3,4,5,6,7,8,9]

    df['month'] = df.index.month
    df=df.groupby('month').resample('5A').mean()
    # df=df.groupby('month').rolling(window = 5, min_periods=3).mean()
    df = df.drop('month', 1)
    settings = {}
    groups = ['group' + str(_id) for _id in range(1,11) ]

    for col in df.columns:
        settings[col]= {}
        settings[col]['dash']=None
        settings[col]['color']=None
        settings[col]['legend']=None

        
    for model in settings.iterkeys():
        if scen1 not in model :
            settings[model]['dash'] = 'solid'
        else: 
            settings[model]['dash'] = 'dashdot'
            
    for model, group in zip(settings.iterkeys(),groups):
        settings[model]['group']=group
    # settings

    fig = tools.make_subplots(rows=1, cols=len(month_ls), shared_yaxes=True,horizontal_spacing = 0.01 ,subplot_titles=month_ls)
    first = [Scatter(x=df.loc[(month_nb[0])].index , y = df.loc[(month_nb[0])][model],line = Line(width=1,dash=settings[model]['dash']),mode='lines',name=model,text=model,hoverinfo='y+text',legendgroup = settings[model]['group'],showlegend=True) for model in df.columns]
    traces = [[Scatter(x=df.loc[(month)].index , y = df.loc[(month)][model],line = Line(width=1,dash=settings[model]['dash']),mode='lines',text=model,name=model,hoverinfo='y+text',legendgroup = settings[model]['group'],showlegend=False) for model in df.columns] for month in month_nb[1:]]
    traces.insert(0,first)
    for data,x in zip(traces,range(1,len(month_ls)+1)) :
        for trace in data :
            fig.append_trace(trace,1,x)
    fig['layout'].update( title='Five Years Monthly Average Temperatures for CMIP3 %s Models and CMIP5 %s Models'%(scen1.upper(),scen2.upper()))
    plot_url = iplot(fig, filename='multiple-subplots-shared-yaxes')
    plot_html, plotdivid, width, height = _plot_html(fig, False, "", True, '100%', 800,"")
    html_start = """
    <html>
    <head>
      <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>"""
    html_end = """
    <center><a title="PR-SRESA1B-RCP60" href="https://www.snap.uaf.edu/webshared/jschroder/Climate/pr-sresa1b-rcp60.html">PR-SRESA1B-RCP60</a>&nbsp;&nbsp;<a title="PR-SRESA2-RCP85" href="https://www.snap.uaf.edu/webshared/jschroder/Climate/pr-sresa2-rcp85.html">PR-SRESA2-RCP85</a>&nbsp;&nbsp;<a title="PR-SRESB1-RCP45" href="https://www.snap.uaf.edu/webshared/jschroder/Climate/pr-sresb1-rcp45.html">PR-SRESB1-RCP45</a>&nbsp;&nbsp;<a title="TAS-SRESA1B-RCP60" href="https://www.snap.uaf.edu/webshared/jschroder/Climate/tas-sresa1b-rcp60.html">TAS-SRESA1B-RCP60</a>&nbsp;&nbsp;<a title="TAS-SRESA2-RCP85" href="https://www.snap.uaf.edu/webshared/jschroder/Climate/tas-sresa2-rcp85.html">TAS-SRESA1B-RCP60</a>&nbsp;&nbsp;<a title="TAS-SRESB1-RCP45" href="https://www.snap.uaf.edu/webshared/jschroder/Climate/tas-sresb1-rcp45.html">TAS-SRESB1-RCP45</a></center></body>
    </html>"""

    html_final = html_start + plot_html + html_end
    f = open('/home/UA/jschroder/Desktop/%s-%s-%s.html'%(metric,scen1,scen2), 'w')
    f.write(html_final)
    f.close()
    del pr
if __name__ == '__main__':
    import pandas as pd
    from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
    from plotly.offline.offline import _plot_html
    from plotly import tools
    import numpy as np
    import cufflinks as cf
    from plotly.graph_objs import *
    init_notebook_mode()
    cf.set_config_file(offline=False, world_readable=True)
    import pickle
    output_path = '/workspace/Shared/Users/jschroder/TMP/v4'
    variables = ['pr','tas']
    CMIP5_models = ['MRI-CGCM3','GISS-E2-R' , 'GFDL-CM3', 'NCAR-CCSM4', 'IPSL-CM5A-LR']
    CMIP4_models =  [model.upper() for model in ['cccma-cgcm3-1-t47' , 'gfdl-cm2-1' , 'miroc3-2-medres' , 'mpi-echam5' , 'ukmo-hadcm3']]
    CMIP5_scenario = ['rcp45','rcp60','rcp85']
    CMIP4_scenario = ['sresb1','sresa1b','sresa2']

    colors = ["#b70040",
    "#ff4549",
    "#9b4600",
    "#ffa81a",
    "#fff55c",
    "#018807",
    "#b7f6ff",
    "#012bcb",
    "#ff47d1",
    "#50002e"]

    for scen1,scen2 in zip(CMIP4_scenario,CMIP5_scenario):
        for metric in variables:
            produce_plot(scen1,scen2,metric)















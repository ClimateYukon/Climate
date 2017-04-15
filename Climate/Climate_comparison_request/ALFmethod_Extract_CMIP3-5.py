#Script mostly based on Michael's code from Alfresco post processing module
class NestedDict(dict):
    def __missing__(self, key):
        self[key] = NestedDict()
        return self[key]

class SubDomains( object ):
    '''
    rasterize subdomains shapefile to ALFRESCO AOI of output set
    '''
    def __init__( self, subdomains_fn, rasterio_raster, id_field, name_field, background_value=0, *args, **kwargs ):
        '''
        initializer for the SubDomains object
        The real magic here is that it will use a generator to loop through the 
        unique ID's in the sub_domains raster map generated.
        '''
        import numpy as np
        self.subdomains_fn = subdomains_fn
        self.rasterio_raster = rasterio_raster
        self.id_field = id_field
        self.name_field = name_field
        self.background_value = background_value
        self._rasterize_subdomains( )
        self._get_subdomains_dict( )

    def _rasterize_subdomains( self ):
        '''
        rasterize a subdomains shapefile to the extent and resolution of 
        a template raster file. The two must be in the same reference system 
        or there will be potential issues. 
        returns:
            numpy.ndarray with the shape of the input raster and the shapefile
            polygons burned in with the values of the id_field of the shapefile
        gotchas:
            currently the only supported data type is uint8 and all float values will be
            coerced to integer for this purpose.  Another issue is that if there is a value
            greater than 255, there could be some error-type issues.  This is something that 
            the user needs to know for the time-being and will be fixed in subsequent versions
            of rasterio.  Then I can add the needed changes here.
        '''
        import geopandas as gpd
        import numpy as np

        gdf = gpd.read_file( self.subdomains_fn )
        id_groups = gdf.groupby( self.id_field ) # iterator of tuples (id, gdf slice)

        out_shape = self.rasterio_raster.height, self.rasterio_raster.width
        out_transform = self.rasterio_raster.affine

        arr_list = { value : self._rasterize_id( df, value, out_shape, out_transform, background_value=self.background_value ) for value, df in id_groups }
        self.sub_domains = arr_list
    @staticmethod
    def _rasterize_id( df, value, out_shape, out_transform, background_value=0 ):
        from rasterio.features import rasterize
        geom = df.geometry
        out = rasterize( ( ( g, value ) for g in geom ),
                            out_shape=out_shape,
                            transform=out_transform,
                            fill=background_value )
        return out
    def _get_subdomains_dict( self ):
        import geopandas as gpd
        gdf = gpd.read_file( self.subdomains_fn )
        self.names_dict = dict( zip( gdf[self.id_field], gdf[self.name_field] ) )

def get_mon_year( x ):
    month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-2:]
    return {'month':month, 'year':year, 'fn':x}

def get_mon_year_historical( x ):
    month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-4:-2]
    return {'month':month, 'year':year, 'fn':x}

def return_means( fn, mask_arr ):

    return np.ma.masked_where( mask_arr == 0, rasterio.open( fn ).read(1) ).mean() 

def compute(dic , subdomains, path , domain , variable , gcm = None, scenario = None , model = None, observed = False) :
    '''This function allows to process the return means function on both the GCM data and the observed data
    Some improvement could be made to make it a bit smarter probably. Need to work a bit more on it
    '''
    if observed == True :
        path = os.path.join(path,variable)
        l = glob.glob( os.path.join( path, '*.tif' ) )
        monyear = map( get_mon_year_historical, l )
    else :
        path = os.path.join(path,gcm,scenario,model,variable)
        l = glob.glob( os.path.join( path, '*.tif' ) )
        monyear = map( get_mon_year, l )

    # list the files in the dir
    df = pd.DataFrame( monyear )
    df = df.sort_values(by=['year', 'month'], ascending=[1, 1])

    l = df.fn.tolist()

    pool = mp.Pool( 32 )
    out = pool.map( lambda x: return_means( x,subdomains[domain]) , l )
    pool.close()
    pool.join()

    df['mean'] = out
    df['date'] = df['year'].map(str) + '-' + df['month']
    df = df.set_index(pd.to_datetime(df['date']))
    df = df.drop(['year' , 'month' , 'fn','date'],1)

    if observed == True :
        dic['observed'][variable][domain] = df
    else :
        #Compute the delta from the observed dictionnary for each month
        obs = dic['observed'][variable][domain]
        #use a factor to multiply the observed list as some of the models don't have the same numbers of years
        multiply_factor = len(l)/12
        df['delta'] = np.array( df['mean'].tolist()) - np.array( obs['mean'].tolist() * multiply_factor)

        dic[gcm][scenario][model][variable][domain] = df
    
    return dic


def produce_plot_yearly (dic,subdomains):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines
    import seaborn as sns
    import datetime
    from math import pi
    from bokeh.plotting import figure, show, output_file, vplot, save
    from bokeh.models import HoverTool, BoxSelectTool ,ColumnDataSource
    
    color1 = ["#5480dc",
    "#5ebf49",
    "#a240ae",
    "#abb539",
    "#4a62d8",
    "#538d2a",
    "#9a6ee5",
    "#44c080",
    "#d13e98",
    "#88b769",
    "#de70da",
    "#397f4d",
    "#de406d",
    "#62bf9e",
    "#d54e31",
    "#40c4d8",
    "#e08830",
    "#7d53a8",
    "#cca238",
    "#5b68a8",
    "#71722c",
    "#bb90da",
    "#a0652e",
    "#67a0d8",
    "#b0483f",
    "#299790",
    "#a84b62",
    "#c6a96b",
    "#a25286",
    "#e286b5"]

    color2 = color1*100

    
    def create_df(frame, col, gcm , domain , scenario , model , variable):
            tmp = dic[gcm][scenario][model][variable][domain]['delta']
            frames.append(tmp)
            col.append('%s - %s' %(scenario,model))


    for variable,domain in itertools.product(variables.keys(),subdomains.keys()) :

        frames = []
        col = []
        combo3 = itertools.product([gcms[0]] , scenarios_cmip3 , models_cmip3 )
        combo5 = itertools.product([gcms[1]] , scenarios_cmip5 , models_cmip5 )
        combos = [combo3,combo5]

        _ = [[create_df(frames, col, gcm , domain , scenario , model , variable) for gcm , scenario , model in combo ] for combo in combos]
        
        tas_df = pd.concat(frames,axis = 1)
        tas_df.columns = col

        month = tas_df.index.month
        year = tas_df.index.year


        selector = ((4<= month) & (8>=month))
        tas_df = tas_df[selector]
        tas_df = tas_df[(tas_df.index >= '2006-01-01')&(tas_df.index <= '2099-12-01')]

        _tools_to_show = 'box_zoom,pan,save,hover,resize,reset,tap,wheel_zoom'        

        p = figure(width=1400, height=900,x_axis_type="datetime", tools=_tools_to_show)

        #http://stackoverflow.com/questions/31496628/in-bokeh-how-do-i-add-tooltips-to-a-timeseries-chart-hover-tool    
        #http://comments.gmane.org/gmane.comp.python.bokeh/594

        #This part is used to plot year by year, it is REALLY long to compute but works with line
        #Trying to work with individual tooltips, one for line one for scatter doesnt work well, waiting for request to dig more into it
        # ts_list_of_list = []
        # ts_list_of_list = [tas_df[tas_df.index.year == i].index for i in np.unique(tas_df.index.year)]
        # ts_list_of_list = [[i]*31 for i in ts_list_of_list]
        # ts_list_of_list =  [item for sublist in ts_list_of_list for item in sublist] 
        # vals_list_of_list=[]
        # for j in np.unique(tas_df.index.year):
        #     tmp = [tas_df[tas_df.index.year == j][i].values for i in tas_df.columns]
        #     vals_list_of_list.append(tmp)
        #     del tmp
        # vals_list_of_list =  [item for sublist in vals_list_of_list for item in sublist]

        # a=[tas_df.columns.values]*100
        # a =  [item for sublist in a for item in sublist]

        # for (colr, x, y ,name) in zip(color2, ts_list_of_list, vals_list_of_list,a):
        #     s1 = p.line(x, y,color= colr)
        #     s1 = p.line(x, y,source= ColumnDataSource({ 'Model': name}),color= colr)
        #     p.add_tools(HoverTool(renderers=[s1], tooltips=[("Model" , "@Model"),]))




        ts_list_of_list = []
        for i in range(0,len(tas_df.columns)):
            ts_list_of_list.append(tas_df.index.T)
        vals_list_of_list=[]
        vals_list_of_list = tas_df.values.T.tolist()

        # Define colors because otherwise multi_line will use blue for all lines...

        p.multi_line(ts_list_of_list, vals_list_of_list, alpha = 0.2,line_color=color1)




        # THEN put  scatter one at a time on top of each one to get tool tips (HACK! lines with tooltips not yet supported by Bokeh?) 
        for (name, series) in tas_df.iteritems():
            # need to repmat the name to be same dimension as index
            name_for_display = np.tile(name, [len(tas_df.index),1])

            source = ColumnDataSource({'x': tas_df.index, 'y': series.values, 'series_name': name_for_display})
            source.add(tas_df.index.to_series().apply(lambda d: d.strftime('%Y-%m')), 'Date')
            # trouble formating x as datestring, so pre-formating and using an extra column. It's not pretty but it works.

            s2 =p.scatter('x', 'y', source = source,size=8, fill_alpha=0.1, line_color=None)     
            p.add_tools(HoverTool(renderers=[s2], tooltips= [("Series", "@series_name"),("Date", "@Date"), ("Value", "@y"),]))
            hover = p.select(dict(type=HoverTool))
            # hover.tooltips = [("Series", "@series_name") ,("Value", "@y"),]
            # hover.mode = 'mouse'

        # p.legend.orientation = "top_left"
        if variable == 'tas' :
            hover.tooltips = [("Series", "@series_name"),("Date", "@Date"), ("Value", "@y"),]
            hover.mode = 'mouse'
            p.title = 'Average Deltas Temperature Values by season and decade From PRISM baseline (1961-1990) '
            p.grid.grid_line_alpha=0.3
            p.xaxis.axis_label = 'Average Deltas Temperature Values by season and decade'
            p.yaxis.axis_label = 'Temperature (C)'
        else :
            hover.tooltips = [("Series", "@series_name"), ("Date", "@Date"), ("Value", "@y{0.00%}"),]
            hover.mode = 'mouse'
            p.title = 'Average Deltas Precipitation Values by season and decade From PRISM baseline (1961-1990) '
            p.grid.grid_line_alpha=0.3
            p.xaxis.axis_label = 'Average Deltas Precipitation Values by season and decade'
            p.yaxis.axis_label = 'Percentage of change'

        p.xaxis.major_label_orientation = pi/4
        out = os.path.join( output_path,  'try_%s.html'%(variable) )
        output_file(out, title="GCM comparison for %s"%(variable))
        save(p)

def produce_plot_decade(dic,subdomains):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines
    import seaborn as sns
    import datetime
    from math import pi
    from bokeh.plotting import figure, show, output_file, vplot, save
    from bokeh.models import HoverTool, BoxSelectTool ,ColumnDataSource
    
    color1 = ["#5480dc",
    "#5ebf49",
    "#a240ae",
    "#abb539",
    "#4a62d8",
    "#538d2a",
    "#9a6ee5",
    "#44c080",
    "#d13e98",
    "#88b769",
    "#de70da",
    "#397f4d",
    "#de406d",
    "#62bf9e",
    "#d54e31",
    "#40c4d8",
    "#e08830",
    "#7d53a8",
    "#cca238",
    "#5b68a8",
    "#71722c",
    "#bb90da",
    "#a0652e",
    "#67a0d8",
    "#b0483f",
    "#299790",
    "#a84b62",
    "#c6a96b",
    "#a25286",
    "#e286b5"]

    color2 = color1*100

    def create_df(frame, col, gcm , domain , scenario , model , variable):
            tmp = dic[gcm][scenario][model][variable][domain]['delta']
            frames.append(tmp)
            col.append('%s - %s' %(scenario,model))


    for variable,domain in itertools.product(variables.keys(),subdomains.keys()) :

        frames = []
        col = []
        combo3 = itertools.product([gcms[0]] , scenarios_cmip3 , models_cmip3 )
        combo5 = itertools.product([gcms[1]] , scenarios_cmip5 , models_cmip5 )
        combos = [combo3,combo5]

        _ = [[create_df(frames, col, gcm , domain , scenario , model , variable) for gcm , scenario , model in combo ] for combo in combos]
        
        tas_df = pd.concat(frames,axis = 1)
        tas_df.columns = col
        
        #Using a selector to query the df
        month = tas_df.index.month
        year = tas_df.index.year
        selector = ((4<= month) & (8>=month))
        tas_df = tas_df[selector]
        tas_df = tas_df[tas_df.index <= '2099-12-01']
        
        frames = []
        ts_list_of_list = []
        dic_helper = {}
        for i in np.unique(tas_df.index.month) :
            tmp= tas_df[tas_df.index.month == i]
            tmp = tmp.groupby((tmp.index.year //10)*10).mean()
            tmp.index=tmp.index.map(str) + '-' + str(i)
            dic_helper[i] = tmp
            frames.append(tmp)

        tas_df = pd.concat(frames)


        # tas_df = tas_df[(tas_df.index >= '2006-01-01')&(tas_df.index <= '2099-12-01')]

        _tools_to_show = 'box_zoom,pan,save,hover,resize,reset,tap,wheel_zoom'        
        
        factors = [str(x) for x in tas_df.index]
        p = figure(width=1600, height=900,x_range=factors, tools=_tools_to_show)
        
        #http://stackoverflow.com/questions/31496628/in-bokeh-how-do-i-add-tooltips-to-a-timeseries-chart-hover-tool    
        #http://comments.gmane.org/gmane.comp.python.bokeh/594

        #This part is used to plot year by year, it is REALLY long to compute but works with line
        #Trying to work with individual tooltips, one for line one for scatter doesnt work well, waiting for request to dig more into it
        # ts_list_of_list = []
        # ts_list_of_list = [tas_df[tas_df.index.year == i].index for i in np.unique(tas_df.index.year)]
        # ts_list_of_list = [[i]*31 for i in ts_list_of_list]
        # ts_list_of_list =  [item for sublist in ts_list_of_list for item in sublist] 
        # vals_list_of_list=[]
        # for j in np.unique(tas_df.index.year):
        #     tmp = [tas_df[tas_df.index.year == j][i].values for i in tas_df.columns]
        #     vals_list_of_list.append(tmp)
        #     del tmp
        # vals_list_of_list =  [item for sublist in vals_list_of_list for item in sublist]

        # a=[tas_df.columns.values]*100
        # a =  [item for sublist in a for item in sublist]

        # for (colr, x, y ,name) in zip(color2, ts_list_of_list, vals_list_of_list,a):
        #     s1 = p.line(x, y,color= colr)
        #     s1 = p.line(x, y,source= ColumnDataSource({ 'Model': name}),color= colr)
        #     p.add_tools(HoverTool(renderers=[s1], tooltips=[("Model" , "@Model"),]))

        


        for i,frames in dic_helper.iteritems() :
            tmp_df = frames
            ts_list_of_list = []
        
            for i in range(0,len(tmp_df.columns)):
                ts_list_of_list.append(tmp_df.index.T)
        
            vals_list_of_list=[]
            vals_list_of_list = tmp_df.values.T.tolist()

        
        # Define colors because otherwise multi_line will use blue for all lines...

            p.multi_line(ts_list_of_list, vals_list_of_list, alpha = 0.8,line_color=color1)




        # THEN put  scatter one at a time on top of each one to get tool tips (HACK! lines with tooltips not yet supported by Bokeh?) 
        for (name, series) in tas_df.iteritems():
            # need to repmat the name to be same dimension as index
            name_for_display = np.tile(name, [len(tas_df.index),1])

            source = ColumnDataSource({'x': tas_df.index, 'y': series.values, 'series_name': name_for_display})
   
            # trouble formating x as datestring, so pre-formating and using an extra column. It's not pretty but it works.

            s2 =p.scatter('x', 'y', source = source,size=9, fill_alpha=0.2, line_color=None, hover_color='olive', hover_alpha=1.0)     
            p.add_tools(HoverTool(renderers=[s2], tooltips= [("Series", "@series_name"),("Date", "@x"), ("Value", "@y"),]))
            hover = p.select(dict(type=HoverTool))
            # hover.tooltips = [("Series", "@series_name") ,("Value", "@y"),]
            # hover.mode = 'mouse'

        # p.legend.orientation = "top_left"
        if variable == 'tas' :
            hover.tooltips = [("Series", "@series_name"),("Date", "@x"), ("Value", "@y"),]
            hover.mode = 'mouse'
            p.title = 'Average Deltas Temperature Values by summer months and decade From PRISM baseline (1961-1990) '
            p.grid.grid_line_alpha=0.3
            p.xaxis.axis_label = 'Average Deltas Temperature Values by summer months and decade'
            p.yaxis.axis_label = 'Temperature (C)'
        else :
            hover.tooltips = [("Series", "@series_name"), ("Date", "@x"), ("Value", "@y"),]
            hover.mode = 'mouse'
            p.title = 'Average Deltas Precipitation Values by summer months and decade From PRISM baseline (1961-1990) '
            p.grid.grid_line_alpha=0.3
            p.xaxis.axis_label = 'Average Deltas Precipitation Values by summer months and decade'
            p.yaxis.axis_label = 'Precipitation (mm)'

        p.xaxis.major_label_orientation = pi/4
        out = os.path.join( output_path,  'DRAFT_ALF_dynamic_decade_comparison_%s.html'%(variable) )
        output_file(out, title="GCM comparison for %s"%(variable))
        save(p)     

if __name__ == '__main__':
    import rasterio, fiona, glob, os
    import numpy as np
    import pandas as pd
    from pathos import multiprocessing as mp
    import pickle
    import itertools

    shp_fn = '/workspace/Shared/Users/jschroder/ALFRESCO_SERDP/Data/Domains/Boreal.shp'
    hist_path = '/home/UA/jschroder/historical_AkCAN_Prism_cropped/'

    Base_path = '/Data/Base_Data/Climate/AK_CAN_2km/projected/'
    gcms = ['AR4_CMIP3_models','AR5_CMIP5_models'] #add projected
    scenarios_cmip5 = ['rcp60','rcp85','rcp45']
    scenarios_cmip3 = ['sresa1b','sresa2','sresb1']
    models_cmip5 = ['MRI-CGCM3','GISS-E2-R' , 'GFDL-CM3', 'CCSM4', 'IPSL-CM5A-LR']
    models_cmip3 = ['cccma-cgcm3-1-t47', 'gfdl-cm2-1' , 'miroc3-2-medres' , 'mpi-echam5' , 'ukmo-hadcm3']
    variables = {'pr': 'Precipitation', 'tas' : 'Temperature'}
    ref = '/Data/Base_Data/Climate/AK_CAN_2km/projected/AR4_CMIP3_models/sresa1b/cccma-cgcm3-1-t47/pr/pr_total_mm_ar4_cccma_cgcm3_1_sresa1b_01_2001.tif'
    shp_id = 'Id'
    shp_name = 'Name'
    output_path = '/workspace/Shared/Users/jschroder/TMP/'
    dic_output = "/workspace/Shared/Users/jschroder/TMP/multimodal_extraction_tom-scott_request.p"


    subdomains = SubDomains( shp_fn, rasterio.open(ref), shp_id , shp_name ).sub_domains

    #Probably better way to do it than using this class but works for now
    #Creates a dict with [gcm][scenario][model][variable][domain] 
    # dic = NestedDict()

    # combo3 = itertools.product([gcms[0]] , subdomains.keys() , scenarios_cmip3 , models_cmip3 , variables.keys())
    # combo5 = itertools.product([gcms[1]] , subdomains.keys() , scenarios_cmip5 , models_cmip5 , variables.keys())
    # combos = [combo3,combo5]

    # #Compute the observed data, note that the PRISM data have been cropped in order to allow domain selection 
    # #Potential solution would be to include test and crop on the fly : https://github.com/EarthScientist/etc/blob/master/crop_raster_rasterio.py
    # obs_combo = itertools.product(subdomains.keys(), variables)
    # _ = [ compute( dic , subdomains , hist_path , domain , variable, observed = True) for domain , variable in obs_combo]

    # #Modeled data
    # _ = [[compute( dic , subdomains , Base_path , domain , variable , gcm , scenario , model, observed = False) for gcm , domain , scenario , model , variable in combo ] for combo in combos]
    # del combos,combo3, combo5
    # pickle.dump( dic, open( dic_output, "wb" ) )

    #for plotting debugging without re-extracting
    dic = pickle.load(open(dic_output, 'rb'))
    # produce_plot_yearly(dic,subdomains)
    produce_plot_decade(dic,subdomains)
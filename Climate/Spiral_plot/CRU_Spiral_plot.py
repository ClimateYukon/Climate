import geopandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm
from rasterio import features
from affine import Affine
import numpy as np
import xarray as xray
import pandas as pd
import datetime as dt
import os
from __future__ import division
import seaborn as sns


sns.set(style="whitegrid")
data_out = '/workspace/Shared/Users/jschroder/TMP/spiral_Arctic/'
# import matplotlib.pyplot as plt
if not os.path.exists( data_out ):
	os.mkdir( data_out )
# %matplotlib inline

def transform_from_latlon(lat, lon):
    lat = np.asarray(lat)
    lon = np.asarray(lon)
    trans = Affine.translation(lon[0], lat[0])
    scale = Affine.scale(lon[1] - lon[0], lat[1] - lat[0])
    return trans * scale

def rasterize(shapes, coords, latitude='latitude', longitude='longitude',
              fill=np.nan, **kwargs):
    """Rasterize a list of (geometry, fill_value) tuples onto the given
    xray coordinates. This only works for 1d latitude and longitude
    arrays.
    """
    transform = transform_from_latlon(coords[latitude], coords[longitude])
    out_shape = (len(coords[latitude]), len(coords[longitude]))
    raster = features.rasterize(shapes, out_shape=out_shape,
                                fill=fill, transform=transform,
                                dtype=float, **kwargs)
    spatial_coords = {latitude: coords[latitude], longitude: coords[longitude]}
    return xray.DataArray(raster, coords=spatial_coords, dims=(latitude, longitude))

# this shapefile is from natural earth data
# http://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/
states = geopandas.read_file('/workspace/Shared/Users/jschroder/TMP/circum_region.shp')
#states = geopandas.read_file('/workspace/Shared/Users/jschroder/TMP/ne_10m_admin_1_states_provinces.shp')

#For Arctic :
states = geopandas.read_file('/workspace/Shared/Users/jschroder/TMP/circum_region.shp')
us_states = states
state_ids = {k: i for i, k in enumerate(us_states.adm1_code)}
shapes = zip(us_states.geometry, range(len(us_states)))
ds = xray.open_dataset('/workspace/Shared/Users/jschroder/TMP/cru_ts3.23.1901.2014.tmp.dat.nc')
ds['states'] = rasterize(shapes, ds.coords, longitude='lon', latitude='lat')
arr = ds.tmp.where(ds.states == state_ids['Arctic'])

# For Alaska :
# states = geopandas.read_file('/workspace/Shared/Users/jschroder/TMP/ne_10m_admin_1_states_provinces.shp')
# us_states = states.query("admin == 'United States of America'").reset_index(drop=True)
# state_ids = {k: i for i, k in enumerate(us_states.woe_name)}
# shapes = zip(us_states.geometry, range(len(us_states)))
# ds = xray.open_dataset('/workspace/Shared/Users/jschroder/TMP/cru_ts3.23.1901.2014.tmp.dat.nc')
# ds['states'] = rasterize(shapes, ds.coords, longitude='lon', latitude='lat')
# arr = ds.tmp.where(ds.states == state_ids['Alaska']).sel(lon=slice(-175, -125), lat=slice(53, 73))


d = {'mean' : [arr[i].mean().data.item() for i in range(0, len(arr.time))]}
base_df = pd.DataFrame(d,index=arr.time)


#select the dictionnary in order to calculate monthly anomalies through 1900 1930
anomalies = base_df['01/01/1900':'12/31/1930']
anomalies_dic = {k:anomalies[anomalies.index.month == k].mean().item() for k in anomalies.index.month }
base_df['anomalies'] = [(value - anomalies_dic[row.month]).item() for row, value in base_df.iterrows()]

df2 = base_df
def f(dfa):
    dfa = dfa.copy()
    dfa['Year'] = dfa.index.year
    dfa['Month'] = dfa.index.month
    dfa['Day'] = dfa.index.day
    return dfa

full_df = f(df2)
def year_frac2(row):
    y = int(row['Year'])
    m = int(row['Month'])
    d = int(row['Day'])
    if np.isnan([y, m, d]).any():
        return np.nan
    else:
        return dt.datetime(y, m, d).timetuple().tm_yday/dt.datetime(y, 12, 31).timetuple().tm_yday*2*np.pi


full_df['degree'] = full_df.apply(year_frac2, axis=1)
full_df = full_df.reset_index()

# full_df.to_csv('/workspace/Shared/Users/jschroder/TMP/full_df.csv')
# full_df = pd.read_csv( '/workspace/Shared/Users/jschroder/TMP/full_df.csv', index_col=0 )

cm = plt.get_cmap('rainbow')
#cm = sns.color_palette("cubehelix", 8)
length = full_df.degree.__len__()
color = [cm(i/(length-1)) for i in range(length-1)]
fig = plt.figure()
ax = plt.subplot(111, projection='polar')
period = 1
for i in range(length):
	ax.plot(full_df.degree[i*period:((i+1)*period+1)], full_df.anomalies[i*period:((i+1)*period+1)], color = color[i*period],alpha=0.5)
	ax.set_thetagrids(np.linspace(360/24, 360*23/24, 12))
	ax.set_theta_direction('clockwise')
	ax.set_theta_offset(np.pi/2)
	ax.xaxis.set_ticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
	ax.set_rmin(min(full_df.anomalies)*1.1)
	ax.set_rmax(max(full_df.anomalies)*1.1)
	ax.set_yticks([-10,-5,0,5,10])
	ax.set_yticklabels(["-10c","-5c","0c","+5c","+10c"])

	fig.subplots_adjust(top=.88)
	plt.title('%s - Arctic Regions'%full_df.Year[i*period],fontsize = 15,y=1.08)
	if i == 0 :
		fig.text(0.01, 0.01, 'CRU TS v. 3.23 - Anomalies (1900-1930)', fontsize=11)
	else:
		pass
	plt.savefig(os.path.join(data_out, dt.datetime(full_df.Year[i*period], full_df.Month[i*period], full_df.Day[i*period]).strftime("%Y%m%d")+'.png'),figsize = ( 14, 8 ), dpi=150)

plt.close()






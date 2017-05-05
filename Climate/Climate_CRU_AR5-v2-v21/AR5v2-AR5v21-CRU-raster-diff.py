
def get_mon_year( x ):
    month, year = os.path.splitext( os.path.basename( x ) )[0].split( '_' )[-2:]
    return {'month':month, 'year':year, 'fn':x}

def list_files(path):
    l = glob.glob( os.path.join( path, '*.tif' ) )
    monyear = list(map( get_mon_year, l ))
    df = pd.DataFrame( monyear )
    df = df.sort_values(by=['year', 'month'], ascending=[1, 1])
    l = df.fn.tolist()
    return l

def diff(f):
    import rasterio
    import numpy as np
    file1,file2 = f
    f1 = rasterio.open(file1).read(1)
    f2 = rasterio.open(file2).read(1)
    return np.subtract(f1,f2)

def diff2(f):
    import rasterio
    import numpy as np
    file1,file2 = f

    f1 = rasterio.open(file1).read(1)
    f2 = rasterio.open(file2).read(1)
    
    if np.array_equal(f1,f2) : pass
    else : return print('{}Different!!'.format(file1))

if __name__ == '__main__':
    import pandas as pd
    import rasterio
    import numpy as np
    import glob
    from pathos import multiprocessing as mp
    import os
    import itertools
    paths = ['/Data/Base_Data/Climate/AK_CAN_2km_v2/',
    '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/downscaled/']
    
    out = '/workspace/Shared/Users/jschroder/TMP/'
    variables = ('pr','tas')
    models = ['GISS-E2-R', 'GFDL-CM3' , 'IPSL-CM5A-LR' , 'MRI-CGCM3' , 'NCAR-CCSM4' ]
    scenarios = [ 'rcp45' , 'rcp60' , 'rcp85']
    CRU_paths = ['/Data/Base_Data/Climate/AK_CAN_2km_v2/CRU_TS323/historical' , '/workspace/Shared/Tech_Projects/DeltaDownscaling/project_data/downscaled/ts40/historical']



    # for i in itertools.product( models , scenarios , variables) :
    #     pathls = [os.path.join( p, *i) for p in paths]
    #     print( pathls)
    #     _ = [list_files(i) for i in pathls]
    #     l = [[a1,a2]for a1,a2 in zip(_[0],_[1])]

    #     pool = mp.Pool( 32 )
    #     array = pool.map(diff,l)
    #     pool.close()
    #     pool.join()


    for i in  variables :
        pathls = [os.path.join( p, i) for p in CRU_paths]
        print( pathls)
        _ = [list_files(i) for i in pathls]
        l = [[a1,a2]for a1,a2 in zip(_[0],_[1])]

        pool = mp.Pool( 32 )
        array = pool.map(diff,l)
        pool.close()
        pool.join()

        ok = np.sum(array,axis=0)

        meta = rasterio.open(l[0][0]).meta

        with rasterio.open(os.path.join(out,'_'.join(['CRU',i]) + '.tif'),'w',**meta) as dst :
            dst.write_band(1,ok.astype(rasterio.float32))




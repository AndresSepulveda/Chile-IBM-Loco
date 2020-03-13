import geopandas
import xarray as xr
import numpy as np

# criteria to find sedimentation event
sed_crit = 0.1

ranges = {1: ['01062008', '20062008'], 2: ['02062008', '20062008'],
          3: ['20112015', '01042016'], 4: ['01052016', '01082016'],
          5: ['03082015', '01082016']}


def get_paths(experiment):
    startdate, enddate = ranges[experiment]
    base = r'results'
    return [base + '/loco_opendrift_%s_to_%s_experiment_%s.nc' % (startdate, enddate, experiment)]


def first_n_nan(arr):
    return np.ma.flatnotmasked_edges(arr)[0]


def last_n_nan(arr):
    return np.ma.flatnotmasked_edges(arr)[-1]


def get_lat(d, n):
    # find lat of the particle at the sedimentation time 
    return d.lat[n][get_sed(d, n)]


def get_lon(d, n):
    # find lat of the particle at the sedimentation time 
    return d.lon[n][get_sed(d, n)]


def get_latlon(d):
    arr = np.ma.masked_invalid(d.dif_depth.values)
    arr2 = np.ma.masked_greater(arr, sed_crit)
    # fin lat of the particle at the sedimentation time 
    if arr2.count() == 0:
        return None
    else:
        sed = first_n_nan(arr2)
    return [d.lat[sed].values, d.lon[sed].values]


def get_start(d, n):
    # find index of the release event, 
    # first non masked element
    arr = np.ma.masked_invalid(d.dif_depth[n].values)
    return first_n_nan(arr)


def get_dif_depth(data):
    # find differences between floor depth and particle depth for each trajectory     
    # ! find first non nan at first and cut the rest 
    data = data.where(data.z != 'nan')
    data = data.where(data.z != np.nan)
    data = data.where(data.sea_floor_depth_below_sea_level != 'nan', drop=True)
    data['dif_depth'] = data.sea_floor_depth_below_sea_level - data.z
    return data


def get_df(path):
    df = xr.open_dataset(path)
    df['z'] = df['z'] * -1.
    return df.where(df.status > -1, drop=True)


if __name__ =='__main__':
    print(get_paths([1, 2], experiment=1))

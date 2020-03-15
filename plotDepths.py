from typing import List, Any

import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from pandas.plotting import register_matplotlib_converters
import seaborn as sns
import utils
import time
import glob
import dask

sed_crit = 0.1
sns.set()
register_matplotlib_converters()


def plt_part(df, axis, color):
    df['dif_depth'] = df.sea_floor_depth_below_sea_level - df.z

    grp = df.groupby('trajectory')
    all_depths: List[Any]=[]
    for k, ds in enumerate(grp):  # loop over trajectories
        df = ds[1]
        x = df.time[:]
        z = df.z[:]

        arr = np.ma.masked_invalid(z)
        start_index = utils.first_n_nan(arr)
        end_index = utils.last_n_nan(arr)
        all_depths.append(z.values)
        axis.plot(x, z, '-', color=color, linewidth=0.5, alpha=0.5, zorder=9)
        axis.plot(x[end_index], z[end_index].values, 'bo', markersize=2.5, zorder=10)
        axis.plot(x[start_index], z[start_index].values, 'ko', markersize=2.5, zorder=10)

    # axis.set_title('Distibution of particles (type {})'.format(p_part))
    frmt = '%b/%d'
    axis.xaxis.set_major_formatter(mdates.DateFormatter(frmt))
    axis.set_ylabel('Depth, m')
    axis.set_xlabel('Month,day of the release')
    axis.set_ylim(-60, 0)
    return all_depths

# axis.set_xlim(startdate, '2000-02-15T00:00:00')


def call_make_plot_mf():
    fig = plt.figure(figsize=(11.69, 8.27), dpi=200,
                     facecolor='white')
    gs = gridspec.GridSpec(3, 2, width_ratios=[3, 1])
    gs.update(left=0.08, right=0.98, top=0.96, bottom=0.08,
              wspace=0.13, hspace=0.37)

    ax1 = fig.add_subplot(gs[0])
    ax1_1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[2])
    ax2_1 = fig.add_subplot(gs[3])

    with xr.open_mfdataset(utils.get_paths(1), concat_dim='time', combine='nested') as ds:  #
        df_exp1 = ds.load()
    with xr.open_mfdataset(utils.get_paths(2), concat_dim='time', combine='nested') as ds:  #
        df_exp2 = ds.load()

    df_exp1 = df_exp1.where(df_exp1.status > -1, drop=True)
    df_exp2 = df_exp2.where(df_exp2.status > -1, drop=True)

    print("Plotting the trajectories....")
    all_depths_1 = plt_part(df_exp1, ax1, color='#dc3d5f')
    all_depths_2 = plt_part(df_exp2,ax2, color='b')

    for axis2 in (ax1_1, ax2_1):
        axis2.set_title('Loco depths')

    bins = np.arange(-60, 0, 1)

    all_depths_1_flat=[depth for sub_list in all_depths_1 for depth in sub_list]
    all_depths_2_flat = [depth for sub_list in all_depths_2 for depth in sub_list]
    ax1_1.hist(all_depths_1_flat, bins=bins, density=True, color='r')
    ax2_1.hist(all_depths_2_flat, bins=bins, density=True)


    plt.savefig('Figures/Loco_trajectories_and_histograms_w_advection_turbulence.png',format = 'png')
    print("---  It took %s seconds to run the script ---" % (time.time() - start_time))
    plt.show()


if __name__ == '__main__':
    start_time = time.time()
    call_make_plot_mf()

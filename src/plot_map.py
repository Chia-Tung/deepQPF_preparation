import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

print(f"cartopy data path: {cartopy.config['data_dir']}")


def get_colorbar():
    cwbRR = mpl.colors.ListedColormap(['#FFFFFF', '#9CFCFF', '#03C8FF', '#059BFF', '#0363FF',
                                       '#059902', '#39FF03', '#FFFB03', '#FFC800', '#FF9500',
                                       '#FF0000', '#CC0000', '#990000', '#960099', '#C900CC',
                                       '#FB00FF', '#FDC9FF'])
    bounds = [0, 1, 2, 5, 10, 15, 20, 30, 40,
              50, 70, 90, 110, 130, 150, 200, 300]
    norm = mpl.colors.BoundaryNorm(bounds, cwbRR.N)
    return cwbRR, norm


def background_map(lon_min: float, lon_max: float, lat_min: float, lat_max: float):
    # https://stackoverflow.com/questions/33942233/how-do-i-change-matplotlibs-subplot-projection-of-an-existing-axis
    # shows the truth of plt.axes. Another website: https://zhajiman.github.io/post/cartopy_introduction/
    fig, geo_axes = plt.subplots(1, 1, figsize=(5, 3), dpi=200, facecolor='w',
                                 subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0.)})
    # feature
    # geo_axes.stock_img() # low resolution land illustration
    geo_axes.add_feature(cfeature.LAND, edgecolor='black')
    geo_axes.add_feature(cfeature.OCEAN.with_scale('10m'))
    geo_axes.add_feature(cfeature.COASTLINE.with_scale('10m'), lw=1)
    # tick
    geo_axes.set_xticks(np.linspace(lon_min, lon_max, 5),
                        crs=ccrs.PlateCarree())
    geo_axes.set_yticks(np.linspace(lat_min, lat_max, 5),
                        crs=ccrs.PlateCarree())
    geo_axes.xaxis.set_major_formatter(
        LongitudeFormatter(zero_direction_label=False))
    geo_axes.yaxis.set_major_formatter(LatitudeFormatter())
    geo_axes.tick_params(axis='both', which='major', labelsize=5)
    # range
    geo_axes.set_extent(
        [lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    # gridline
    geo_axes.gridlines(xlocs=np.linspace(lon_min, lon_max, 5), ylocs=np.linspace(lat_min, lat_max, 5),
                       draw_labels=False, linestyle='--')
    return fig, geo_axes


def plot(x_data, y_data, z_data, lon_min: float, lon_max: float, lat_min: float, lat_max: float):
    cmap, norm = get_colorbar()
    fig, geo_axes = background_map(lon_min, lon_max, lat_min, lat_max)
    # data
    geo_axes.pcolormesh(x_data, y_data, z_data, edgecolors='none',
                        shading='auto', norm=norm, cmap=cmap)
    fig.show()
"""

A few utility functions needed for the convection tracking and the processing of WRF data

"""
import numpy as np 
import xarray as xr

def subset_data(fname, XLAT, XLONG):
    """
    Function to select IWP variable and subsets region to Amazon river basin before loading into memory.  
    """

    ds = xr.open_dataset(fname) # chunks={'south_north': 50, 'west_east': 50})
    data = ds.IWP.squeeze()
    
    minlon, maxlon = -85, -50 
    minlat, maxlat = -15, 10 

    # subset region 
    lat_min_idx = np.unravel_index(np.argmin(np.abs(XLAT - minlat)), XLAT.shape)
    lat_max_idx = np.unravel_index(np.argmin(np.abs(XLAT - maxlat)), XLAT.shape)
    lon_min_idx = np.unravel_index(np.argmin(np.abs(XLONG - minlon)), XLONG.shape)
    lon_max_idx = np.unravel_index(np.argmin(np.abs(XLONG - maxlon)), XLONG.shape)
    

    south_north_min_idx, _ = lat_min_idx
    south_north_max_idx, _ = lat_max_idx
    _, west_east_min_idx = lon_min_idx
    _, west_east_max_idx = lon_max_idx
    
    
    subset = data.isel(
        south_north=slice(south_north_min_idx, south_north_max_idx + 1),
        west_east=slice(west_east_min_idx, west_east_max_idx + 1)
)

    # load data into memory 
    amazon_region = subset.compute()

    return amazon_region

    


def subset_coords(ds_coords, XLAT, XLONG):
    minlon, maxlon = -85, -50 
    minlat, maxlat = -15, 10 

    # subset region 
    lat_min_idx = np.unravel_index(np.argmin(np.abs(XLAT - minlat)), XLAT.shape)
    lat_max_idx = np.unravel_index(np.argmin(np.abs(XLAT - maxlat)), XLAT.shape)
    lon_min_idx = np.unravel_index(np.argmin(np.abs(XLONG - minlon)), XLONG.shape)
    lon_max_idx = np.unravel_index(np.argmin(np.abs(XLONG - maxlon)), XLONG.shape)

    south_north_min_idx, _ = lat_min_idx
    south_north_max_idx, _ = lat_max_idx
    _, west_east_min_idx = lon_min_idx
    _, west_east_max_idx = lon_max_idx

    
    xlat= ds_coords.XLAT.squeeze()
    xlong= ds_coords.XLONG.squeeze()
    
    lats = xlat.isel(
        south_north=slice(south_north_min_idx, south_north_max_idx + 1),
        west_east=slice(west_east_min_idx, west_east_max_idx + 1))
    
    lons = xlong.isel(
        south_north=slice(south_north_min_idx, south_north_max_idx + 1),
        west_east=slice(west_east_min_idx, west_east_max_idx + 1))
 
    # load data
    latitudes = lats.compute()
    longitudes = lons.compute()

    return latitudes.data, longitudes.data
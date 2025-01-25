"""

Script to track convection in one month of hourly cloud ice water path data in a WRF simulation over South America (horizontal resolution: 4km). 

The tracking is constrained to the extent of the Amazon river basin. 

The tracking library tobac is used: https://github.com/tobac-project/tobac (tobac version: 1.5.5)

Contact: kukulies@ucar.edu


"""
import sys 
import numpy as np 
import xarray as xr 
from pathlib import Path 
from tqdm import tqdm 
from datetime import datetime 
from utils import subset_data, subset_coords

import tobac 
print(tobac.__version__)

# year and month to be processed (input parameters on command line)
year = str(sys.argv[1])
month = str(sys.argv[2]).zfill(2)


#### TRACKING PARAMETERS #### 

dxy,dt= 4000, 3600

# parameters for feature detection                                                           
parameters_features = {}
parameters_features['threshold']=[0.24] # thresholds for ice water path 
parameters_features['target']='maximum'
parameters_features['n_min_threshold']= 1 
parameters_features['statistic'] = {"feature_min_iwp": np.nanmin, 'feature_max_iwp': np.nanmax, 'feature_mean_iwp': np.nanmean}

# parameters for linking 
parameters_linking={}
parameters_linking['v_max']=1e2
parameters_linking['stubs']= 2 
parameters_linking['adaptive_stop']=0.2
parameters_linking['adaptive_step']=0.95
parameters_linking['method_linking']= 'predict'

# parameters for segmentation 
parameters_segmentation = {}
parameters_segmentation['threshold']= 0.25 # kg/m2                    
parameters_segmentation['target'] = "maximum"
parameters_segmentation['statistic'] = {"min_iwp": np.nanmin, 'max_iwp': np.nanmax, 'mean_iwp': np.nanmean}

#### WRF DATA #### 

# get WRF data for one month 
wrf_output = Path(str('/glade/campaign/univ/uiuc0017/chliu/WRF4KM_2000-2020/wrf2d_wrf3d/'+year+'/'))
monthly_files = list(wrf_output.glob(str('wrf2d*'+year+ '-' + month +'*')))
monthly_files.sort()
print(len(monthly_files), 'files for month ', month)

# get the constant fields for WRF simulation, contains coordinates 
ds_coords = xr.open_dataset( Path('/glade/campaign/univ/uiuc0017/chliu/WRF4KM_2000-2020/wrf2d_wrf3d/wrfconstants_SAAG_20yr.nc')) 
XLAT= ds_coords.XLAT.values.squeeze()
XLONG= ds_coords.XLONG.values.squeeze()
latitudes, longitudes = subset_coords(XLAT, XLONG)

for fname in tqdm(monthly_files): 
    amazon_region_t = subset_data(fname)
    if fname == monthly_files[0]:
        monthly_data = amazon_region_t 
    else:
        monthly_data = xr.concat([monthly_data, amazon_region_t], dim = 'Time') 

# modify time variable to make compatible with tobac 
input_data = monthly_data.rename({"XTIME": "time"})
input_data['time']= monthly_data.XTIME.values


### CONVECTION TRACKING ON ONE MONTH OF INPUT DATA ###

# 1. FEATURE DETECTION
features = tobac.feature_detection_multithreshold(input_data ,dxy, **parameters_features)
print('feature detection done', datetime.now())

# 2. TRACKING 
tracks = tobac.linking_trackpy(features, input_data, dt, dxy, **parameters_linking)    
print('tracking done', datetime.now())
# remove cells that are not connected over time 
tracks = tracks[tracks.cell != -1]

# 3. SEGMENTATION
mask, tracks = tobac.segmentation_2D(tracks, input_data, dxy, **parameters_segmentation)
print('segmentation done', datetime.now())


























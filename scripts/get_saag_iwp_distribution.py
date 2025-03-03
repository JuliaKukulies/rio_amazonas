"""
This script derives histograms of hourly IWP values from the SAAG WRF 4km simulation over 20 years.
Email: kukulies@ucar.edu 

"""
import numpy as np
import xarray as xr
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

##### directories #####
saag_data = Path('/glade/campaign/univ/uiuc0017/chliu/WRF4KM_2000-2020/wrf2d_wrf3d/')
out_dir = Path('/glade/campaign/mmm/c3we/CPTP_kukulies/saag/IWP/')

##### bins for histograms #####
bin_edges_iwp = np.logspace(-3, 2, 101) 
for year in np.arange(2000,2021):
    # looping through months  
    for month in np.arange(1,13):
        year = str(year)
        month = str(month).zfill(2)
        if Path(out_dir / str('iwp_log_counts_' + year + month + '.npy' )).is_file():
            continue
        else:
            # read in hourly WRF files
            year_dir = saag_data / year
            hourly_files = list( year_dir.glob('*wrf2d*'))
            for fname in hourly_files:
                ds= xr.open_dataset(fname)
                iwp = ds.IWP.squeeze().data
                iwp_hist, _ = np.histogram(iwp, bins = bin_edges_iwp)
                if fname == hourly_files[0]: 
                    hist = iwp_hist
                else:
                    hist += iwp_hist
            np.save(out_dir / str('iwp_log_counts_' + year + month  ), hist)
            print('derived histogram for', year, ' ', month, flush = True) 



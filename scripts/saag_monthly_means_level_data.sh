#!/bin/bash

# Define input and output directories
input_dir="/glade/campaign/univ/uiuc0017/chliu/WRF4KM_2000-2020/wrf2d_wrf3d"
output_dir="/glade/campaign/mmm/c3we/CPTP_kukulies/saag/winds"

# Loop over each year directory
for year_dir in $input_dir/201[0-9]; do
    if [ -d "$year_dir" ]; then
	year=$(basename $year_dir)
	files=($year_dir/wrf3d_d01_${year}-*_*) # hourly file in year directory 

	# Create a list organized with all files belonging to a certain month together
	declare -a month_files
	# make sure the list of monthly files is empty 
	monthly_files=()
	for file in "${files[@]}"; do
	    month=$(basename "$file" | cut -d'-' -f2)
	    month=$((10#$month)) 
	    month_files["$month"]+="$file "
	done
	
	for month in {1..12}; do
	    output_file_monthly="$output_dir/upper_winds_monthly_mean_${year}_${month}.nc"
	    # Check if the output file already exists
	    if [ -e "$output_file_monthly" ]; then
		echo "The file '$output_file_monthly' exists. Continuing to the next iteration."
		continue  # Skip the rest of the loop and move to the next iteration
	    fi
	    if [ ! -z "${month_files[$month]}" ]; then
		#echo "${month_files[$month]}"
		echo "Processing month ${month} for year ${year}"
		# array with files only for this month 
		month_wind_files=()

		for file in ${month_files[$month]}; do
		    filename=$(basename "$file")
		    filename_noext="${filename%.*}"

		    # Extract variable and save to the output directory with a unique filename
		    output_file="${output_dir}/${filename_noext}_upper_winds_${month}.nc"

		    # select specific level of file 
		    ncks -d bottom_top,34 -v U,V "$file" upper_temp_uv.nc
		    ncks -d bottom_top_stag,34 -v W "$file" upper_temp_w.nc
		    ncks -A upper_temp_w.nc upper_temp_uv.nc
		    mv upper_temp_uv.nc "$output_file"
		    rm upper_temp_w.nc 
		    
		    # Append the processed file to the list for the month
		    month_wind_files+=("$output_file")
		done
		
		# Compute the monthly mean var using ncea
		ncea -h "${month_wind_files[@]}" "$output_dir/upper_winds_monthly_mean_${year}_${month}.nc"

		# Clean up the temporary var files for this month
		rm -f "${month_wind_files[@]}"
	    fi
	done

	# Now calculate the yearly mean by averaging the monthly files
	#monthly_files_for_year=($output_dir/upper_winds_monthly_mean_${year}_*.nc)
	#ncea -h "${monthly_files_for_year[@]}" "$output_dir/upper_winds_yearly_mean_${year}.nc"

	echo "all rpocessing done for year ${year}."
	#"Yearly mean horizontal and vertical winds for ${year} calculated. Output saved to $output_dir/upper_winds_yearly_mean_${year}.nc"
    fi
done





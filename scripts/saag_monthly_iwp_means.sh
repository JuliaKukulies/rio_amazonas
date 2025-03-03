#!/bin/bash

# Define input and output directories
input_dir="/glade/campaign/univ/uiuc0017/chliu/WRF4KM_2000-2020/wrf2d_wrf3d/"
output_dir="/glade/campaign/mmm/c3we/CPTP_kukulies/saag/IWP/"

# Loop over each year directory
for year_dir in $input_dir/201[0-9]; do
    if [ -d "$year_dir" ]; then
	year=$(basename $year_dir)
	files=($year_dir/wrf2d_d01_${year}-*_*) # hourly file in year directory 

	# Create a list organized with all files belonging to a certain month together
	declare -a month_files
	monthly_files=()
	for file in "${files[@]}"; do
	    month=$(basename "$file" | cut -d'-' -f2)
	    month=$((10#$month)) 
	    month_files["$month"]+="$file "
	    
	    #month=$(basename $file | cut -d'-' -f2)
	    #month=$(echo $month | sed 's/^0//')
	    #month_files["$month"]+=("$file")
	done


	for month in {1..12}; do
	    if [ ! -z "${month_files[$month]}" ]; then
		echo "Processing month ${month} for year ${year}"
		# array with files only for this month 
		month_iwp_files=()

		for file in ${month_files[$month]}; do
		    filename=$(basename "$file")
		    filename_noext="${filename%.*}"

		    # Extract variable IWP and save to the output directory with a unique filename
		    output_file="${output_dir}/${filename_noext}_IWP_${month}.nc"
		    ncks -v IWP "$file" "$output_file"
		    
		    # Append the processed IWP file to the list for the month
		    month_iwp_files+=("$output_file")
		done

		# Compute the monthly mean IWP using ncea
		ncea -h "${month_iwp_files[@]}" "$output_dir/IWP_monthly_mean_${year}_${month}.nc"

		# Clean up the temporary IWP files for this month
		rm -f "${month_iwp_files[@]}"
	    fi
	done

	# Now calculate the yearly mean by averaging the monthly files
	monthly_files_for_year=($output_dir/IWP_monthly_mean_${year}_*.nc)
	ncea -h "${monthly_files_for_year[@]}" "$output_dir/IWP_annual_mean_${year}.nc"

	echo "Yearly mean IWP for ${year} calculated. Output saved to $output_dir/IWP_annual_mean_${year}.nc"
    fi
done





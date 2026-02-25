The folders are organized as follows:
- clean_month_agg: contains number of movements between source, destination pairs aggregated by month. Contains 12 files, where each pertains to a unique month 
- clean_month_raw: contains source,destination pairs belonging to each month. does not include weights; only details source and destination
- clean_season_agg: contains number of movements between source, destination pairs aggregated by season. Contains 4 files, corresponding to each season
- clean_season_raw:  contains source,destination pairs belonging to each season. does not include weights; only details source and destination and corresponding month of occurence
- inc_dat: contains the files for the two infection datasets: raw_data.csv and ma_data.csv

The individual files are detailed as follows:
  - yearly_clean_agg.csv: contains movements of source, destination pairs aggregated by year
  - yearly_clean_raw.csv: contains source,desintation pairs that occur every year, separeated by month and year
  - pub_clean_prop_dat.csv: property-id dataset, cotnains property-id values, hectare size, and whether the property is used for calibration or not




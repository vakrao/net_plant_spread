The folders are organized as follows:
- **clean_month_agg**: contains 12 files, where each pertains to a unique month. Each file shows the number of movements between source-destination pairs occurring in that unique month.
- **clean_season_agg**: contains 4 files, where each pertains to each season. Each file shows the number of movements between source-destination pairs occurring in that season.
- **incidence_data**: contains the two files with the infection incidence data: raw_data.csv and ma_data.csv, where "ma" stands for moving average and "raw" stands for the extracted interpolated incidence data from XXXX{hhtps://XXX}.

The individual files are detailed as follows:
  - **raw_individual_data.csv**: contains individual movements, where the source property id and the destination property id are provided for each movement, as well as the year, season, and month when it occurred
  - **pub_clean_prop_dat.csv**: this dataset contains property ids, hectare size of each property, and binary values to denote whether the property is used in calibration




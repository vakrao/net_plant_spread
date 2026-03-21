Directory Description
-----------------
The `data_gen` folder contains the scripts used to generate the aggregated monthly, seasonal, and yearly data. The raw movements found in `data/raw_individual_data` are used to generate the aggregated data files. All files are saved in the `data/` folder. 


- **month_df_create.py** &rarr; creates aggregated monthly movement network based on the source,dest, and month when they occur. Creates individual networks for each month, saved in `clean_month_agg/`. 

- **season_df_create.py** &rarr; creates aggregated season movement network based on the source,dest, and month when they occur. Every month pertains to the corresponding season that they belong to. Uses data from `clean_month_agg/` to create seasonal networks which are  saved in `clean_season_agg/`. 

- **year_df_create.py** &rarr; creates yearly movement network based on the source and dest when movement occurs. Creates one yearly network saved in `data/yearly_clean_agg.csv`. 


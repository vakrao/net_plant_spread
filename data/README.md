### Data Description ###
--------------
Mobility data from the biosecurity company is used in our metapopulation model.  Our model assumes that data will be organized in one of three ways: monthly, seasonal, or yearly, depending on the aggregation used. To achieve the results similar to the paper, use the data in this folder the the notebooks in the notebook/manuscript_notebooks folder. For more information on how we filtered the data, refer to the paper. The implementation of the filtering can be observed in the filter_seeds function in src/helpers.py, and in the find_viable function in src/graph_helpers.py
## Folder Organization ## 
--------------------
The folders are organized as follows:
- **clean_month_agg**: contains 12 files, where each pertains to a unique month. Each file shows the number of movements between source-destination pairs occurring in that unique month.
- **clean_season_agg**: contains 4 files, where each pertains to each season. Each file shows the number of movements between source-destination pairs occurring in that season.
- **inc_data**: contains the two files with the infection incidence data: raw_data.csv and ma_data.csv, where "ma" stands for moving average and "raw" stands for the extracted interpolated incidence data from a report by Greer and Saunders. Refer to page 3 in the report for the number of infected orchards {https://kvh.org.nz/assets/documents/About-KVH-tab/The_Costs_of_Psa_V_to_the_New_Zealand_Kiwifruit_Industry__Wider_Community_Report.pdf}

The individual files are detailed as follows:
  - **raw_individual_data.csv**: contains individual movements, where the source property id and the destination property id are provided for each movement, as well as the year, season, and month when it occurred
  - **yearly_clean_agg.csv**: contains aggregated yearly movements, where the source property id and the destination property id are given for each aggregated movement, as well as the frequency of movements that occur 
  - **pub_clean_prop_dat.csv**: this dataset contains property ids, hectare size of each property, and binary values to denote whether the property is used in calibration




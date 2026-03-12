Folder Organization
-------------
The src/ folder contains all the code needed to run the model. 

- **mod_si.py**: Main model script E_runner.py calls functions in this file to run the S-I model

- **E_runner.py**: experiment runner script. Process .yaml files and saves .csv files to results/ folder

- **find_seeds.py**: identifies which seeds are in the connected component and flagged for calibration

- **gen_heatmap.py**: contains helper functions for calculating RMSE and incidence statistics

- **graph_helpers.py**: contains helper functions used in manuscript_notebooks/.

- **helpers.py**:contains functions used for finding best-configurations and for finding viable seeds

- **plots.py**: creates posterior distributions and heatmap dataframe 

- **spatial_helpers.py**: contains functions used to generate spatial figures

- **vary_sm.py**: Runner script for varying start month of outbreak


Sub-Folders
-----------

**data-gen/** &rarr;   contains the code used to generate the files used in the clean_season_agg and clean_month_agg folders

**notebook/** &rarr; contains example jupyter notebooks used to visualize lines of best fit


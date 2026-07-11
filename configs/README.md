Configuration Worklow
--------------
The workflow for data creation works as follows:

Config files create data &rarr; data used for figures &rarr; `.yaml` files correspond to figures

All the `.yaml` files generate the data used for the graph
shown in `src/notebook/fig_graph_configs.ipynb` The best-fitting configurations are reported in Table III. 

Available Configurations
---------------------
We have also included the folder `src/notebook/manuscript_configs/`, which contains the config files to create the data used to generate the figures in the paper. 


- **best_raw_season.yaml** &rarr; generates infection data for configuration that fits the raw data best using seasonal network

- **best_raw_month.yaml** &rarr; generates infection data for configuration that fits the raw data best using monthly network

- **best_raw_year.yaml** &rarr; generates infection data for configuration that fits the raw data best using yearly network

- **best_ma_season.yaml** &rarr; generates infection data for configuration that fits the MA(moving-average) data best using seasonal network

- **best_ma_month.yaml** &rarr; generates infection data for configuration that fits the MA data best using monthly network

-**best_ma_year.yaml** &rarr; generates infection data for configuration that fits the MA data best using yearly network


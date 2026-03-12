The workflow for data creation works as follows: 

    .yaml files create data &rarr; data used for figures &rarr; .yaml files correspond to figures

All the .yaml files generate the data used for the graph
shown in fig_graph_configs.ipynb. The best-fitting configurations are reported in Table III. 

We have also included the folder manuscript_configs/, which contains the config files to create the data
used to generate the figures in the paper. 


-**best_raw_season.yaml**: generates infection data for configuration that fits the raw data best using seasonal network

-**best_raw_month.yaml**: generates infection data for configuration that fits the raw data best using monthly network

-**best_raw_year.yaml**: generates infection data for configuration that fits the raw data best using yearly network

-**best_ma_season.yaml**: generates infection data for configuration that fits the MA(moving-average) data best using seasonal network

-**best_ma_month.yaml**: generates infection data for configuration that fits the MA data best using monthly network

-**best_ma_year.yaml**: generates infection data for configuration that fits the MA data best using yearly network


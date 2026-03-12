Within this folder, we specify which .yaml file correspond to the figure in the manuscript. 

Specific .yaml files were used to generate the gridsearch data, and the lines of best fit. 

The save_folder parameter is left blank, fill it in with the folder of your choosing in the home folder.
Here's an example, for the lin_Y_D.yaml file:
    - save_folder: "../results/lin_Y/"

manuscript_configs/
- (Fig S2,4): lin_Y_D.yaml specifies parmeters for the linear gridsearch for yearly aggregation  
- (Fig S1): log_Y_D.yaml specifies parmeters for the logistic gridsearch for yearly aggregation
- (Fig S2): lin_S_D.yaml specifies parmeters for the linear gistic gridsearch for yearly aggregation
- (Fig S1): log_S_D.yaml specifies parmeters for the logistic gridsearch for yearly aggregationl
- (Fig S1): lin_M_D.yaml specifies parmeters for the linear gridsearch for monthly aggregation 
- (Fig S1): log_M_D.yaml specifies parmeters for the logistic gridsearch for monthly aggregation 
- (Fig S8): valpha_s.yaml specfies parameters for the experiment varying alpha value for best seasonal configuration
- (Fig 6): vd_s.yaml specifies parameters for experiment varying detection threshold for best seasonal configuration
- (Fig 7): vsm_m.yaml specifies parameters for experiment varying month when infection using best monthly configuration

Using the gridsearch configurations, we visualize Figures 3 and 4. 
To generate Figure 5, refer to the function calc_neigh_monthly_spread in the src/ folder.



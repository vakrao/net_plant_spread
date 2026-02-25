.yaml files create data -> data used for figures -> .yaml files correspond to figures

Within the manuscript_configs/ folder, each .yaml file creates the data needed for a figure in the manuscript. 
Specific .yaml files were used to generate the gridsearch data, and the lines of best fit. 

manuscript_configs/
- (Fig S2): lin_Y_D.yaml specifies parmeters for the linear gridsearch for yearly aggregation  
- (Fig S1): log_Y_D.yaml specifies parmeters for the logistic gridsearch for yearly aggregation
- (Fig S2): lin_S_D.yaml specifies parmeters for the linear gistic gridsearch for yearly aggregation
- (Fig S1): log_S_D.yaml specifies parmeters for the logistic gridsearch for yearly aggregationl
- (Fig S1): lin_M_D.yaml specifies parmeters for the linear gridsearch for monthly aggregation 
- (Fig S1): log_M_D.yaml specifies parmeters for the logistic gridsearch for monthly aggregation 
- (Fig S8): valpha_s.yaml specfies parameters for the experiment varying alpha value for best seasonal configuration
- (Fig 6): vd_s.yaml specifies parameters for experiment varying detection threshold for best seasonal configuration
- (Fig 7): vsm_m.yaml specifies parameters for experiment varying month when infection using best monthly configuration

Using the gridsearch configurations, we visualize Figures 3 and 4



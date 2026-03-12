#from cdlib import algorithms,viz
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import seaborn as sns
#from scipy.stats import entropy
import hashlib
from datetime import datetime,timedelta
import logging


CLEAN_DATA_PATH = "../../data/raw_individual_data.csv"
PROP_PATH = "../../data/clean_prop_dat.csv"
CLEAN_AGG_FOLDER = "../../data/clean_month_agg/"


def generate_time_weights(full_data,init_year):
    # but! using 2022
    time = 0
    for month in range(1,13):
        # filter based on start/end date
        filt_df = full_data[full_data["month"] == month]
        filt_df = filt_df.reset_index()
        if month < 10:
            month_str = "0"+str(month)
        else:
            month_str = str(month)
        #filt_df_title = f"{month_str}_{init_year}_raw.csv"
        #filt_df_title = CLEAN_RAW_FOLDER+filt_df_title
        #raw_df = filt_df.drop(columns=["index","Unnamed: 0"])
        #raw_df.to_csv(filt_df_title)

        # now, count movements occuring between two properties
        weight_df = filt_df.groupby(["source","dest"]).count().reset_index()
        weight_df= weight_df.rename(columns={"year":"weight"})
        df_title = f"{month_str}_{init_year}.csv"
        weight_df_title = CLEAN_AGG_FOLDER+df_title
        weight_df = weight_df.drop(columns=["index","Unnamed: 0","month","season"])
        weight_df.to_csv(weight_df_title)
    return filt_df


if __name__=="__main__":
    # this creates the dataframe that we need
    full_df = pd.read_csv(CLEAN_DATA_PATH)
    init_year = "2022"
    weight_df = generate_time_weights(full_df,init_year)

#from cdlib import algorithms,viz
import networkx as nx
import igraph as ig
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import seaborn as sns
from scipy.stats import entropy
from datetime import datetime,timedelta
import logging
import hashlib


PROP_PATH = "../data/clean_prop_dat.csv"
CLEAN_AGG_FOLDER = "../data/clean_season_agg/"
CLEAN_MONTH_FOLDER = "../data/clean_month_agg/"



def create_season_df(y):
    s_name = ["SM","AT","WT","SP"]
#    s_name = ["SM","AT","SP","WT"]
    sum_months = ["12","01","02"]
    aut_months = ["03","04","05"]
    wint_months = ["06","07","08"]
    spr_months = ["09","10","11"]
    all_seasons = {"SM":sum_months,"AT":aut_months,"WT":wint_months,"SP":spr_months}
    # loop through all the month files
    # each month corresponds to 30 day increments
    # we join three of these together to form a season
    # each number roughly corresponds to a month
    for seas in all_seasons:
        season_dat = []
        season_months = all_seasons[seas]
        for j,m in enumerate(season_months):
            month_name = CLEAN_MONTH_FOLDER+m+"_2022.csv"
            month_dat = pd.read_csv(month_name)
            season_dat.append(month_dat)
        curr_season = seas
        season_df = pd.concat(season_dat)
#        season_fn = CLEAN_AGG_FOLDER+curr_season+"_2022.csv"
#        season_df.to_csv(season_fn)
        # now, count weights  properly
        weight_df = season_df.groupby(["source","dest"])["weight"].sum().reset_index()
        weight_df= weight_df.rename(columns={"year":"weight"})
        df_title = f"{curr_season}_{init_year}.csv"
        weight_df_title = CLEAN_AGG_FOLDER+df_title
        weight_df.to_csv(weight_df_title)
    return weight_df

if __name__=="__main__":
    init_year = "2022"
    # this creates the dataframe that we need
    create_season_df(init_year)

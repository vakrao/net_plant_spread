#from cdlib import algorithms,viz
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import seaborn as sns
from scipy.stats import entropy
from datetime import datetime,timedelta
import logging
import hashlib


CLEAN_DATA_PATH = "../../data/raw_individual_data.csv"
CLEAN_AGG_FILE= "../../data/clean_year_agg.csv"

   
if __name__=="__main__":
    year_raw = pd.read_csv(CLEAN_DATA_PATH)
    year_agg= year_raw.groupby(["source","dest"]).count().reset_index()
    year_agg= year_agg.rename(columns={"year":"weight"})
    weight_df = year_agg.drop(columns=["Unnamed: 0","month","season"])
    weight_df.to_csv(CLEAN_AGG_FILE)


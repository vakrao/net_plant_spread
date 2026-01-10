#from cdlib import algorithms,viz
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import seaborn as sns
#from scipy.stats import entropy
from datetime import datetime,timedelta
import logging


FULL_DATA_PATH = "../params/cleaned_2022_impute.csv"
PROP_PATH = "../params/2024_prop_dat.csv"
CALIB_PATH = "../params/psa_cumulative_numbers.csv"
save_folder = "../params/month_tau/"
date_folder = "../params/month_raw/"

def create_month_df(init_year,industry):
    full_df = pd.read_csv(FULL_DATA_PATH)
    #filters dataframe based on date and industry
    full_df["date"] = pd.to_datetime(full_df['date'].str.strip(),format="%Y-%m-%d %H:%M:%S.%f") 
#    full_df["date"] = pd.to_datetime(full_df["date"])
    full_df["month"] = full_df["date"].dt.month
    full_df["year"] = full_df["date"].dt.year
#    start_date = (datetime.strptime(init_date,'%Y-%m-%d'))
    full_df = full_df[full_df["year"] == init_year]
    weight_df = generate_time_weights(full_df,industry,save_folder)
    #weight_df = weight_df.rename(columns={"SOURCE_PROPERTY_ID":"source","DEST_PROPERTY_ID":"dest"})
    #weight_df = weight_df.drop(columns=["month","date","index","Unnamed: 0","DEST_JOB_ID"])
    #full_title = industry.lower()+str(tau)+".csv"
    #weight_df.to_csv(full_title)

def generate_time_weights(full_data,industry,save_folder):
    # but! using 2022
    time = 0
    orchard_ids = find_farms(industry)
    for month in range(1,13):
        # filter based on start/end date
        filt_df = full_data[full_data["month"] == month]
        filt_df = filt_df[filt_df["SOURCE_PROPERTY_ID"].isin(orchard_ids)]
        filt_df = filt_df[filt_df["DEST_PROPERTY_ID"].isin(orchard_ids)]
        filt_df = filt_df.reset_index()
        if month < 10:
            month_str = "0"+str(month)
        else:
            month_str = str(month)
        filt_df_title = f"{month_str}_{init_year}_raw.csv"
        filt_df_title = date_folder+filt_df_title
        raw_df = filt_df.drop(columns=["index","Unnamed: 0"])
        raw_df.to_csv(filt_df_title)

        # now, count movements occuring between two properties
        weight_df = filt_df.groupby(["SOURCE_PROPERTY_ID","DEST_PROPERTY_ID"]).count().reset_index()
        weight_df= weight_df.rename(columns={"year":"weight"})
        df_title = f"{month_str}_{init_year}.csv"
        weight_df_title = save_folder+df_title
        weight_df = weight_df.rename(columns={"SOURCE_PROPERTY_ID":"source","DEST_PROPERTY_ID":"dest"})
        weight_df = weight_df.drop(columns=["month","date","index","Unnamed: 0","DEST_JOB_ID"])
        weight_df.to_csv(weight_df_title)
    return filt_df

def find_farms(industry_type):
    # check if all properties in prop_produce_combo are re
   # properties = pd.read_csv("../params/prop_produce_combo.csv")
    properties = pd.read_csv("../params/prop_dat.csv")
    prop_df = pd.read_csv("../params/prop_types.csv")
    prop_types = properties["PROPERTY_TYPES"]
    prop_ids = properties["PROPERTY_ID"]
    prop_ids = list(prop_ids)
    i = 0
    indus_farms = list(prop_ids)
    if industry_type != "all":
        indus_farms = []
        indus_prop_df = prop_df.query("INDUSTRY == @industry_type")
        indus_prop_types_id = list(indus_prop_df["ID"])
        indus_prop_types_id = [int(x) for x in indus_prop_types_id]
        # loop through all properties and record which ones
        # match the industry of choice
        for p in prop_ids:
            spec_prop_types = prop_types[i]
            if type(spec_prop_types) == str:
                spec_all_types = spec_prop_types.split(",")
                spec_all_types = [int(x) for x in spec_all_types]
                for s in spec_all_types:
                    if s in indus_prop_types_id:
                        indus_farms.append(p)
            else:
                spec_prop_types = prop_types[i]
                if spec_prop_types in indus_prop_types_id:
                    indus_farms.append(p)
            i += 1
    return indus_farms

# write check function for data



if __name__=="__main__":
    init_year = 2022
    industry = "Horticulture"
    # this creates the dataframe that we need
    create_month_df(init_year,industry)

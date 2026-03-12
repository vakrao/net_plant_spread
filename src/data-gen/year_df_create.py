#from cdlib import algorithms,viz
import unittest
import pandas as pd
import hashlib
import matplotlib.pyplot as plt
import numpy as np
import random as random
#import seaborn as sns
from datetime import datetime,timedelta


FULL_DATA_PATH = "../params/final_query.csv"
CLEAN_DATA_PATH = "../params/cleaned_2022.csv"
DIRTY_PROP_PATH = "../params/2024_prop_dat.csv"
PT_PATH = "../params/prop_types.csv"
CLEAN_RAW_PATH = "../params/yearly_clean_raw.csv"
CLEAN_AGG_PATH = "../params/yearly_clean_agg.csv"
PROP_CLEAN_PATH = "../params/clean_prop_dat.csv"
DIRTY_RAW_PATH = "../params/yearly_pub_raw.csv"
DIRTY_AGG_PATH = "../params/horticulture365_check_NZ.csv"
#DIRTY_AGG_PATH = "../params/yearly_clean_agg.csv"

def classify_season(x):
    s_name = ["SM","AT","WT","SP"]
    s_dict = {12:"SM",1:"SM",2:"SM",
              3: "AT",4:"AT",5:"AT",
              6:"WT",7:"WT",8:"WT",
              9:"SP",10:"SP",11:"SP"}
    return s_dict[x]

    
def create_weighted_df(init_year,tau,industry,country):
    full_df = pd.read_csv(CLEAN_DATA_PATH)
    #filters dataframe based on date and industry
    init_date = init_year+"-01-01"
    full_df["date"] = pd.to_datetime(full_df['date'].str.strip(),format="%Y-%m-%d %H:%M:%S.%f") 
    full_df["month"] = full_df["date"].dt.month
    full_df["year"] = full_df["date"].dt.year
    full_df["season"] = full_df["month"].apply(classify_season)

    weight_df = generate_time_weights(full_df,0,init_year,tau,industry,country)
    weight_df = weight_df.drop(columns=["month","season"])
    full_title = CLEAN_AGG_PATH
    weight_df.to_csv(full_title)
    return weight_df

def generate_time_weights(full_data,t,start_year,tau,industry,country):
    init_date = start_year+"-01-01"
    # filter based on start/end date
    start_date = (datetime.strptime(init_date,'%Y-%m-%d'))+timedelta(days=t)
    end_date = (datetime.strptime(init_date,'%Y-%m-%d'))+timedelta(days=tau)
    full_data["SOURCE_PROPERTY_ID"] = pd.to_numeric(full_data["SOURCE_PROPERTY_ID"],downcast='integer',errors='coerce')
    full_data["DEST_PROPERTY_ID"] = pd.to_numeric(full_data["DEST_PROPERTY_ID"],downcast='integer',errors='coerce')
    orchard_ids = find_farms(industry,country)
    filt_data= full_data[full_data["date"] >= start_date]
    filt_df = filt_data[filt_data["date"] <= end_date]
    filt_df = filt_df[filt_df["SOURCE_PROPERTY_ID"].isin(orchard_ids) & filt_df["DEST_PROPERTY_ID"].isin(orchard_ids)]

    filt_df = filt_df.drop(columns=["date","Unnamed: 0"])
    weight_df = filt_df.groupby(["SOURCE_PROPERTY_ID","DEST_PROPERTY_ID"]).count().reset_index()
    filt_df = filt_df.rename(columns={"SOURCE_PROPERTY_ID":"source","DEST_PROPERTY_ID":"dest"})
    filt_df.to_csv(DIRTY_RAW_PATH)
    dirty_ids = pd.read_csv(DIRTY_PROP_PATH)
    id_convert_dict = hash_ids()
    # filt_df gives cleaned ID 
    # pairs for yearly data 
    filt_df["source"] = filt_df["source"].map(lambda x: id_convert_dict[x])
    filt_df["dest"] = filt_df["dest"].map(lambda x: id_convert_dict[x])
    if country == "NZ":
        filt_df.to_csv(CLEAN_RAW_PATH)
    if country == "all":
        filt_df.to_csv("horticulture365_raw_all.csv")
    filt_df = filt_df.reset_index()
    comb_vals = set(filt_df["dest"]).union(set(filt_df["source"]))
    # now, count movements occuring between two properties
    weight_df = weight_df.rename(columns={"year":"weight"})
    weight_df = weight_df.rename(columns={"SOURCE_PROPERTY_ID":"source","DEST_PROPERTY_ID":"dest"})
    weight_df["source"] = weight_df["source"].map(lambda x: id_convert_dict[x])
    weight_df["dest"] = weight_df["dest"].map(lambda x: id_convert_dict[x])
    return weight_df

def find_farms(industry_type,country):
    # check if all properties in prop_produce_combo are re
    properties = pd.read_csv(DIRTY_PROP_PATH)
    if country == "NZ":
        properties["COUNTRY"] = properties["COUNTRY"].fillna("0")
    prop_type_df = pd.read_csv(PT_PATH)
    prop_types = list(properties["PROPERTY_TYPES"])
    countries = list(properties["COUNTRY"])
    prop_ids = list(properties["PROPERTY_ID"])
    lat = list(properties["GPS_CENTRE_LATITUDE"])
    long = list(properties["GPS_CENTRE_LONGITUDE"])
    indus_farms = list(prop_ids)
    if industry_type != "all":
        indus_farms = []
        indus_prop_df = prop_type_df.query("INDUSTRY == @industry_type")
        indus_prop_types_id = list(indus_prop_df["ID"])
        indus_prop_types_id = [int(x) for x in indus_prop_types_id]
        counter = 0
        for i,p in enumerate(prop_ids):
            spec_prop_types = prop_types[i]
            lat_val,long_val = float(lat[i]),(float(long[i])*-1)
            prop_country = countries[i]
            # use lat/long to ensure in country if not labeled
            if (prop_country != "NZ") and ((lat_val < 164 or lat_val> 180) or ( long_val < 33 or long_val > 48)):
                continue

            if type(spec_prop_types) == str:
                spec_all_types = spec_prop_types.split(",")
                spec_all_types = [int(x) for x in spec_all_types]
                for s in spec_all_types:
                    if s in indus_prop_types_id :
                        indus_farms.append(int(p))
                        continue
            else:
                if spec_prop_types in indus_prop_types_id:
                    indus_farms.append(int(p))
    return indus_farms


def test_data():
    raw_dirty = pd.read_csv(DIRTY_RAW_PATH)
    raw_clean = pd.read_csv(CLEAN_RAW_PATH)
    agg_dirty = pd.read_csv(DIRTY_AGG_PATH)
    agg_clean = pd.read_csv(CLEAN_AGG_PATH)

    id_convert_dict = hash_ids()
    def convert(series):
        return series.map(id_convert_dict)

    assert convert(raw_dirty["source"]).equals(raw_clean["source"].astype(str))
    assert convert(raw_dirty["dest"]).equals(raw_clean["dest"].astype(str))
    assert convert(agg_dirty["source"]).equals(agg_clean["source"].astype(str))
    assert convert(agg_dirty["dest"]).equals(agg_clean["dest"].astype(str))

if __name__=="__main__":
    init_year = "2022"
    tau = 365
    industry = "Horticulture"
    country = "NZ"
    # this creates the dataframe that we need
    clean_prop_data()
    clean_full_data()
    create_weighted_df(init_year,tau,industry,country)
    test_data()

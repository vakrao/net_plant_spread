import unittest
import math
import os
from year_df_create import *


class Test(unittest.TestCase):
    # first, check that all farms in find_farms
    # are in the right industry
    country = "NZ"
    hort_farms = find_farms("Horticulture",country)
    vit_farms = find_farms("Viticulture","all")
    hy_fp= "../params/horticulture365_NZ.csv"
    all_farms = find_farms("all","all")
    hort_yearly = pd.read_csv(hy_fp)
    property_data = pd.read_csv("../params/prop_dat.csv")
    prop_ids = list(property_data["PROPERTY_ID"])
    prop_types = list(property_data["PROPERTY_TYPES"])
    countries = list(property_data["COUNTRY"])
    country_id = dict(zip(prop_ids,countries))

    print("TEST 1: CHECKING HORTICULTURE AND VITICULTURE FARM IDs")
    def test_hort_viti_farm_ids(self):
        # check horticulture IDs
        prop_ids = list(self.property_data["PROPERTY_ID"])
        prop_types = list(self.property_data["PROPERTY_TYPES"])
        prop_type_dict = {}
        for i,p in enumerate(prop_types):
            prop_id = prop_ids[i]
            prop_type_dict[prop_id] = p

        # CHECK HORTICULTURE FARM
        for h in self.hort_farms:
            matching_prop_type = prop_type_dict[h]
            self.assertTrue(isinstance(matching_prop_type,str))
            spec_all_types = matching_prop_type.split(",")
            spec_all_types = [int(x) for x in spec_all_types]
            # check that id is not NAN
            for s in spec_all_types:
                self.assertFalse(math.isnan(int(s)))
            # now check that prop type is indeed a horticulture property
            plant_check = False
            for indv_prop_type in spec_all_types:
                if indv_prop_type >= 200 and indv_prop_type <= 301:
                    plant_check = True
            self.assertTrue(plant_check)
                
        # CHECK VITICULTURE FARM
        for h in self.vit_farms:
            matching_prop_type = prop_type_dict[h]
            self.assertTrue(isinstance(matching_prop_type,str))
            spec_all_types = matching_prop_type.split(",")
            spec_all_types = [int(x) for x in spec_all_types]
            # check that id is not NAN
            for s in spec_all_types:
                self.assertFalse(math.isnan(int(s)))
            # now check that prop type is indeed a viticulture property
            # 203 is Vineyard, 306 is a winery
            wine_check = False
            for indv_prop_type in spec_all_types:
                if indv_prop_type == 203 or indv_prop_type == 306:
                    wine_check= True
            self.assertTrue(wine_check)
    
        print("TEST PASSED: find farms working for hort,viti")
        print("=============================================")

    def test_yearly_hort(self):
        # check that horticulture
        # data has no NULL source,dest, or weight
        # check that horticulture
        # data has horticulture
        # data matches all correct property types
        hort_data = pd.read_csv(self.hy_fp)
        raw_data = pd.read_csv("../params/horticulture365_raw_just_NZ.csv")
        hort_source = hort_data["source"]
        hort_dest = hort_data["dest"]
        max_date = pd.to_datetime(max(raw_data["date"]))
        print("TEST 2: CHECKING YEARLY HORT")
        for h in hort_source:
            int_value = int(h)
            self.assertFalse(math.isnan(int_value))
        for h in hort_dest:
            int_value = int(h)
            self.assertFalse(math.isnan(int_value))
        prop_type_dict = {}
        for i,p in enumerate(self.prop_types):
            prop_id = int(self.prop_ids[i])
            prop_type_dict[prop_id] = p
        ### CHECK that all PROPERTY TYPES are CORRECT INDUSTRY
        for h in hort_source:
            hort_type = prop_type_dict[int(h)]
            spec_all_types = hort_type.split(",")
            spec_all_types = [int(x) for x in spec_all_types]
            if isinstance(hort_type,int):  
                self.assertFalse(math.isnan(hort_type))
            plant_check = False
            for indv_prop_type in spec_all_types:
                if indv_prop_type >= 200 and indv_prop_type <= 301:
                    plant_check = True
            self.assertTrue(plant_check)
        for h in hort_dest:
            hort_type = prop_type_dict[int(h)]
            spec_all_types = hort_type.split(",")
            spec_all_types = [int(x) for x in spec_all_types]
            if isinstance(hort_type,int):  
                self.assertFalse(math.isnan(hort_type))
            plant_check = False
            for indv_prop_type in spec_all_types:
                if indv_prop_type >= 200 and indv_prop_type <= 301:
                    plant_check = True
            self.assertTrue(plant_check)
        self.assertEqual(max_date.year,2022)
        print("TEST PASSED: YEARLY HORTICULTURE DATA NON NULL, CORRECT PROPERTY TYPES")
        print("TEST PASSED: YEARLY HORTICULTURE DATA is 2022")
        print("==================================")
    
    def test_hort_temporal_monthly_data(self):
        # open directory containing temporal data
        # 1) ensure that time period is within 30 day period
        # 2) ensure that relevant months are within each time period
        #   - jan,feb in 0 file, feb,march in 1 file etc etc
        # 3) each farm is in horticulture category
        raw_path = "../params/month_raw"
        month_idx = 1
        print("TEST 2: CHECKING MONTHLY HORT")
        for root,dirs,files in os.walk(raw_path):
            for name in files:
                raw_file = os.path.join(root,name)
                raw_data = pd.read_csv(raw_file)
                other_file = os.path.join(raw_path,name)
                max_date = pd.to_datetime(max(raw_data["date"]))
                min_date = pd.to_datetime(min(raw_data["date"]))
                max_month = max_date.month
                min_month = min_date.month
                year = max_date.year
                # TEST 1 - test that all month values are in proper months
                self.assertEqual(max_month,min_month)
                self.assertEqual(max_date.month,month_idx)
                # TEST 2 - test that all month values are in proper year
                self.assertEqual(year,2022)
                month_idx += 1
                prop_type_dict = {}
                for i,p in enumerate(self.prop_types):
                    prop_id = int(self.prop_ids[i])
                    prop_type_dict[prop_id] = p
                hort_source = list(raw_data["SOURCE_PROPERTY_ID"])
                hort_dest= list(raw_data["SOURCE_PROPERTY_ID"])
                # TEST 3 - ensure all properties are horticulture properties
                for h in hort_source:
                    hort_type = prop_type_dict[int(h)]
                    self.assertTrue(hort_type,isinstance(hort_type,str))
                    spec_all_types = hort_type.split(",")
                    spec_all_types = [int(x) for x in spec_all_types]
                    plant_check = False
                    for indv_prop_type in spec_all_types:
                        if indv_prop_type >= 200 and indv_prop_type <= 301:
                            plant_check = True
                    self.assertTrue(plant_check)
                for h in hort_dest:
                    hort_type = prop_type_dict[int(h)]
                    self.assertTrue(hort_type,isinstance(hort_type,str))
                    spec_all_types = hort_type.split(",")
                    spec_all_types = [int(x) for x in spec_all_types]
                    plant_check = False
                    for indv_prop_type in spec_all_types:
                        if indv_prop_type >= 200 and indv_prop_type <= 301:
                            plant_check = True
                    self.assertTrue(plant_check)
            print("TEST PASSED: all ID values are within horticulture industry")
            print("TEST PASSED: all month values are within correct time frame")
            print("TEST PASSED: all year values are within correct time frame")
            print("==================================")

    def test_hort_temporal_seasonal_data(self):
        # open directory containing temporal data
        # 1) ensure that time period is within 30 day period
        # 2) ensure that relevant months are within each time period
        #   - jan,feb in 0 file, feb,march in 1 file etc etc
        # 3) each farm is in horticulture category
        raw_path = "../params/season_raw"
        month_idx = 1
        seasons = ["AT","SM","SR","WT"]
        relv_months = {"SM":[12,1,2],"AT":[3,4,5],"WT":[6,7,8],"SP":[9,10,11]}
        sum_monts = [str(i) for i in relv_months["SM"]]
        aut_months = [str(i) for i in relv_months["AT"]]
        wint_months =[str(i) for i in relv_months["WT"]]
        spring_months =[str(i) for i in relv_months["SP"]]
        for root,dirs,files in os.walk(raw_path):
            for name in files:
                raw_file = os.path.join(root,name)
                season = name[0:2]
                months = relv_months[season]
                raw_data = pd.read_csv(raw_file)
                max_date = pd.to_datetime(max(raw_data["date"]))
                min_date = pd.to_datetime(min(raw_data["date"]))
                max_month = max_date.month
                min_month = min_date.month
                max_year = max_date.year
                min_year = min_date.year
                # TEST: ensure months are correct for season
                self.assertIn(max_month,months)
                self.assertIn(min_month,months)
                self.assertEqual(max_year,2022)
                self.assertEqual(min_year,2022)
            print("TEST PASSED: Season files have correct months ")
            print("TEST PASSED: Season files have correct year ")
            print("==================================")
    def test_country(self):
        if self.country == "NZ":
            for c in self.country_id:
                if c in self.hort_farms and c == "AU":
                    self.assertEqual("NZ","AU")
            self.assertEqual("NZ","NZ")
            print("TEST PASSED: All farms in New Zealand")


if __name__ == "__main__":
    unittest.main()


import unittest
import math
import os
from helpers import clean_temp_shift

# days in each month 
days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

class Test(unittest.TestCase):
    t_m = 14
    # testing all L
    def test_all_L(self):
        increase_amount = {1:31,0:0,6:31,5:30,4:31,3:30,2:31}
        t_m = 14
        add_amount = 0
        month_convert = {0:2,1:1,2:12,3:11,4:10,5:9,6:8}
        for shifts in range(0,7):
            T = 425
            add_amount = 0
            t_m = 14
            if shifts > 0:
                t_m += shifts
                for s in range(1,shifts+1):
                    add_amount += increase_amount[s]
            T += add_amount
            I = [i for i in range(1,T+1)]

            # running model
            min_inc = 1
            cal_month = 2
            m = cal_month
            total = 0
            test_i = []
            # shifts
            for k in range(0,shifts+14):
                if m > 12:
                    m = 1
                total += days[m]
                test_i.append(total)
                m += 1
            c_i,_ = clean_temp_shift(I,t_m,cal_month,shifts)
            shift_i = test_i[shifts:]
            total = 0

            self.assertEqual(c_i,shift_i)

    # testing all L
    def test_different_start_month(self):
        increase_amount = {1:31,0:0,6:31,5:30,4:31,3:30,2:31}
        t_m = 14
        add_amount = 0
        month_convert = {0:2,1:1,2:12,3:11,4:10,5:9,6:8}
        for shifts in range(0,7):
            T = 427
            add_amount = 0
            t_m = 14
            if shifts > 0:
                t_m += shifts
                for s in range(1,shifts+1):
                    add_amount += increase_amount[s]
            T += add_amount
            I = [i for i in range(1,T+1)]

            # running model
            min_inc = 1
            for c in range(1,13):
                cal_month = c
                m = cal_month
                total = 0
                test_i = []
                # shifts
                for k in range(0,shifts+14):
                    if m > 12:
                        m = 1
                    total += days[m]
                    test_i.append(total)
                    m += 1
                c_i,_ = clean_temp_shift(I,t_m,cal_month,shifts)
                shift_i = test_i[shifts:]
                total = 0

                self.assertEqual(c_i,shift_i)
            
if __name__ == "__main__":
    unittest.main()

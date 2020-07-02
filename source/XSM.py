import abc
import os

import numpy as np
import pandas


class XSM:
    beta_static_lookup = {
        "C2011-05": 0.455,
        "C2011-07": 0.455,
        "C2011-12": 0.187,
        "C2011-13": 0.012,
        "C2012-13": 0.108,
        "C2013-01": 0.232,
        "C2013-02": 0.140,
        "C2013-03": 0.359,
        "C2013-04": 1.0,
        "C2013-06": 0.817,
        "C2013-07": 0.0,
        "C2013-08": 1.0,
        "C2013-09": 0.92,
        "C2013-10": 1.0,
        "C2013-11": 0.014,
        "C2013-12": 0.32,
        "C2013-13": 0.000,
        "C2013-15": 0.099,
        "C2014-04": 0.223,
        "C2014-05": 0.071,
        "C2014-06": 0.025,
        "C2014-07": 0.444,
        "C2014-08": 0.975
    }

    def __init__(self, data_file):
        if not os.path.isdir("data"):
            os.makedirs("data")
        self.datafile = data_file
        self.dfs = pandas.read_excel(f'data/{data_file}.xlsx', sheet_name=None, skiprows=1)
        self.baselines = self.dfs['Baseline Schedule'][['ID', 'Duration', 'Total Cost']].values
        self.baselines[:,1] = [self.parse_date(x) for x in self.baselines[:,1]]
        self.BAC = self.baselines[0,2]
        self.PD = int(self.dfs['Baseline Schedule']["Duration"][0][:-1])
        self.sheetnames = self.dfs.keys()
        self.tracking_periods = [x for x in self.sheetnames if "TP" in x] # loops over sheetnames
        self.n_tracking_periods = len(self.baselines[1:])

    def parse_date(self, date):
        elms = date.split()
        total_hour = 0
        for elm in elms:
            if elm.endswith("d"):
                total_hour += int(elm[:-1])*24
            elif elm.endswith("h"):
                total_hour += int(elm[:-1])
        return total_hour

    def MAPE(self, ytrue, ypred):
        ytrue = np.array(ytrue) 
        ypred = np.array(ypred)
        error = np.abs((ytrue-ypred)/ytrue) * 100
        mean_error = np.mean(error)
        return mean_error, error 

    def find_column_indices(self, lst_columns, spe_columns):
        if not isinstance(lst_columns, list):
            lst_columns = list(lst_columns)
        return [lst_columns.index(c) if c in lst_columns else -1 for c in spe_columns]

    @abc.abstractmethod
    def forecast(self):
        pass

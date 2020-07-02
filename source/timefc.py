import os
import logging
import numpy as np

from XSM import XSM

class Time(XSM):

    beta_static_lookup = {
        "C2011-05": 0.650,
        "C2011-07": 0.118,
        "C2011-12": 0.000,
        "C2011-13": 0.065,
        "C2012-13": 0.000,
        "C2013-01": 0.023,
        "C2013-02": 0.000,
        "C2013-03": 0.000,
        "C2013-04": 0.129,
        "C2013-06": 0.062,
        "C2013-07": 0.000,
        "C2013-08": 0.691,
        "C2013-09": 0.853,
        "C2013-10": 0.000,
        "C2013-11": 0.085,
        "C2013-12": 0.130,
        "C2013-13": 0.000,
        "C2013-15": 0.159,
        "C2014-04": 0.188,
        "C2014-05": 0.106,
        "C2014-06": 0.028,
        "C2014-07": 0.093,
        "C2014-08": 0.666
    }

    def __init__(self, data_file):
        super().__init__(data_file)
        if not os.path.isdir("logs/times/"):
            os.makedirs("logs/times")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s]:%(name)s:%(message)s")
        file_handler = logging.FileHandler(filename=f"logs/times/{data_file}")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def get_actual_time(self, tp_from, tp_to):
        return (tp_to-tp_from).days

    def forecast(self):
        print(f"PD={self.PD}")
        beta = Time.beta_static_lookup.get(self.datafile)
        T_AT = self.PD/self.n_tracking_periods
        T_ES = self.PD/self.n_tracking_periods
        AT, ES, EACs = 0, 0, []
        tracking = self.dfs["Tracking Overview"]
        for p in range(len(tracking["Name"])):
            actual_duration = np.busday_count(tracking["Start Tracking Period"][p].date(), tracking["Status date"][p].date())
            earned_duration = np.busday_count(tracking["Start Tracking Period"][0].date(), tracking["Earned Schedule (ES)"][p].date())
            AT += actual_duration; ES = earned_duration
            T_AT = beta*actual_duration + (1-beta)*T_AT
            T_ES = beta*earned_duration + (1-beta)*T_ES
            EAC = AT + (self.PD-ES)*(T_AT/T_ES)
            print(f"Predict EAC(t)={EAC}")
            EACs.append(EAC)
        # get last tracking period
        last_tracking = [tp for tp in self.dfs.keys() if "TP" in tp][-1]
        # change header
        dfs = self.dfs[last_tracking]; header = dfs.iloc[1]; dfs = dfs[2:]; dfs.columns = header
        actual_duration = float(dfs["Actual Duration"][2][:-1]) # 188d -> 188.0 for instance
        mape, error = self.MAPE([actual_duration]*len(EACs[:-1]), EACs[:-1])
        print(f"mape={mape} error={error}")

    def time_forecasting(self):
        col2idx = "name tracking_from tracking_to pv ev ac es".split()
        col2idx = {k: i for i, k in enumerate(col2idx)}
        n_actual_tps = len([x for x in self.sheetnames if "TP" in x])
        data = self.dfs["Tracking Overview"].values
        tracking_start_date = data[0, col2idx['tracking_from']]
        tracking_end_date = data[-1, col2idx['es']]
        PD = (tracking_end_date - tracking_start_date).days
        print(f"PD={PD}")
        n_expected_tps = PD / 20
        ats = [0]
        tats = [PD/n_expected_tps]
        ess = [0]
        tess = [PD/n_expected_tps]
        beta = 0.175
        peacs = []
        start_test = False
        for t in range(1, n_actual_tps+1):
            duration = self.get_actual_time(data[t-1, col2idx['tracking_from']], data[t-1, col2idx['tracking_to']]) 
            ats.append(ats[-1]+duration)
            duration = 1 # do not scale duration
            tat = beta*((ats[t]-ats[t-1])/duration) + (1-beta)*tats[t-1]
            tats.append(tat)

            es = data[t-1, col2idx['es']]
            es = PD - (tracking_end_date - es).days
            ess.append(es)
            tes = beta*((ess[t]-ess[t-1])/duration) + (1-beta)*tess[t-1]
            tess.append(tes)

            k = (PD-ess[t])/tes
            eac = ats[t] + k*tat
            print(f"TP {t} - pEAC={eac:.3f}")
            peacs.append(eac)
        print(f"Actual EAC {ats[-1]:.3f}")
        mape, error = self.MAPE([ats[-1]]*len(peacs[:-1]), peacs[:-1])
        print(f"mape={mape} error={error}")
        self.logger.debug(f"Dataset={self.datafile} Static={mape:.2f}")
        return mape, error



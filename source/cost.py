import logging
import os

from XSM import XSM


class Cost(XSM):

    def __init__(self, data_file):
        super().__init__(data_file)
        if not os.path.isdir("logs/costs"):
            os.makedirs("logs/costs")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s]:%(name)s:%(message)s")
        file_handler = logging.FileHandler(filename=f"logs/costs/{data_file}")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def cost_forecasting(self):
        # init trend
        Ts_AC = [self.BAC/self.n_tracking_periods]
        Ts_EV = [self.BAC/self.n_tracking_periods]
        print("T0_AC = T0_EV: ", Ts_AC[0])

        # Col 0 = ID, col 12 = Duration
        beta = XSM.beta_static_lookup[self.datafile]
        ACs = [0] # init AT0 = 0
        t = 1
        EVs = [0]
        EAC_costs = [] # predict project duration
        start_test = False
        for period in self.tracking_periods:
            print("Tracking periods:", period)
            cols = self.find_column_indices(self.dfs[period].values[1], ["ID", "Actual Cost", "Earned Value (EV)", "Planned Value (PV)"])
            data_period = self.dfs[period].values[2:, cols] 
            assert (self.baselines[:,0] == data_period[:,0]).sum() == len(self.baselines), "Wrong permutation!"

            # current trend
            cur_AC = data_period[0,1]
            ACs.append(cur_AC)
            T_AC = beta*(ACs[t] - ACs[t-1]) + (1-beta)*Ts_AC[t-1]
            Ts_AC.append(T_AC)

            EV = data_period[0,2]
            PV = data_period[0,3]
            EVs.append(EV)
            T_EV = beta*(EVs[t] - EVs[t-1]) + (1-beta)*Ts_EV[t-1]
            Ts_EV.append(T_EV)

            if t >= (len(self.tracking_periods)*2/3) and T_EV > 0:
            # if T_EV > 0:
                k = (self.BAC-EVs[t]) / T_EV
                EAC = ACs[t] + k * T_AC
                EAC_costs.append(EAC)
                print("Predict EAC:", EAC)
            # end calculate
            t += 1
        print("Project actual costs: ", data_period[0,1])
        mape, error = self.MAPE([ACs[-1]]*len(EAC_costs[:-1]), EAC_costs[:-1])
        print("MAPE: ", mape)
        self.logger.debug(f"Dataset={self.datafile} Dynamic={mape} Error={error}")
        return error, mape




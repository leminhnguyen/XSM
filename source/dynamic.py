import os

import numpy as np
from matplotlib import pyplot as plt

from XSM import XSM


class DynamicCost(XSM):

    def __init__(self, data_file):
        super().__init__(data_file)
        if not os.path.isdir("figures"):
            os.makedirs("figures")
        plt.style.use("seaborn")

    def forecast(self):
        # init trend
        Ts_AC = [self.BAC/self.n_tracking_periods]
        Ts_EV = [self.BAC/self.n_tracking_periods]
        init_T = self.BAC/self.n_tracking_periods
        print("T0_AC = T0_EV: ", Ts_AC[0])

        def select_best_beta(cur_AC):
            betas = [] # list of tuples (beta, MAPE)
            for beta in np.arange(0.0, 1, 0.05): # e^beta*x
                _ACs, _Ts_AC, predict_ACs = [0], [0], []
                for prev_period in range(0, cur_period):
                    # cur_AC = prev_AC + trend_AC
                    data_prev_period = self.dfs[self.tracking_periods[prev_period]].values[2:, cols]
                    prev_AC = data_prev_period[0, 1]
                    _ACs.append(prev_AC)
                    _T_AC = calculate_current_trend(_ACs, beta, init_T)
                    predict_AC = _ACs[prev_period-1] + (cur_period - prev_period)*_T_AC
                    predict_ACs.append(predict_AC)
                if len(predict_ACs) == 0:
                    error = 0
                else:
                    ytrue = np.array([cur_AC]*len(predict_ACs))
                    ypred = np.array(predict_ACs)
                    error = np.abs((ytrue-ypred)/ytrue) * 100
                    weights = 1 - np.arange(0, 1, 1/len(error))[:len(error)]
                    error = np.sum(error*weights)
                betas.append((beta, error))
            # select best beta
            beta = sorted(betas, key=lambda x: x[1])[0][0]
            return beta

        def calculate_current_trend(ACs, beta, init_T):
            if len(ACs) == 1: return init_T
            prev_T = calculate_current_trend(ACs[:-1], beta, init_T)
            T = beta*(ACs[-1] - ACs[-2]) + (1-beta) * prev_T
            return T

        # Col 0 = ID, col 12 = Duration
        ACs, EVs, EAC_costs, betas = [0], [0], [], []
        t = 1
        cols = self.find_column_indices(self.dfs[self.tracking_periods[0]].values[1], ["ID", "Actual Cost", "Earned Value (EV)", "Planned Value (PV)"])
        for cur_period, period in enumerate(self.tracking_periods):
            print(f"------- Tracking periods: {period} -----------")
            data_period = self.dfs[period].values[2:, cols]
            cur_AC = data_period[0, 1]
            ACs.append(cur_AC)
            # find optimal beta
            beta = select_best_beta(cur_AC)
            print(f"Best beta {beta:.3f}", )
            T_AC = calculate_current_trend(ACs, beta, init_T)
            Ts_AC.append(T_AC)

            EV, PV = data_period[0,2], data_period[0,3]
            EVs.append(EV)
            T_EV = beta*(EVs[t] - EVs[t-1]) + (1-beta)*Ts_EV[t-1]
            Ts_EV.append(T_EV)

            # if t >= (len(self.tracking_periods)*2/3) and T_EV > 0: # dong lenh sai cua k60
            betas.append(beta)
            k = (self.BAC-EVs[t]) / T_EV
            EAC = ACs[t] + k * T_AC
            EAC_costs.append(EAC)
            print(f"Predict EAC: {EAC:.3f}\n")
            t += 1
        print("Project actual costs: ", ACs[-1])
        mape, error = self.MAPE([ACs[-1]]*len(EAC_costs[:-1]), EAC_costs[:-1])
        print(f"Dynamic MAPE: {mape:.2f}")
        print(f"error={error}\n")
        print(f"betas={betas}")
        self.draw_time_series(error, betas)
        return error, mape, ACs[-len(error):], EAC_costs[:-1], betas[:-1] 

    def draw_time_series(self, errors, betas):
        errors = np.append(errors, 0)
        TPs = ["TP" + str(idx) for idx, tp in enumerate(self.tracking_periods)]
        figure, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)

        ax1.set_title("Beta Dynamic")
        ax1.set_xlabel("Tracking Periods")
        ax1.set_ylabel("Beta Dynamic")
        ax1.plot(TPs, betas)

        ax2.set_title("Mape Values")
        ax2.set_xlabel("Tracking Periods")
        ax2.set_ylabel("Mape")
        ax2.plot(TPs, errors)
        plt.show()
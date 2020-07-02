import numpy as np
from matplotlib import pyplot as plt

from XSM import XSM
from timefc import Time


class ReferenceClassTime(XSM):

    PROJECTS = ["C2014-05", "C2014-06", "C2014-07", "C2014-08"]

    def __init__(self, data_file):
        super().__init__(data_file)
        plt.style.use("seaborn")

    def get_actual_time(self, tp_from, tp_to):
        return (tp_to-tp_from).days

    def get_best_beta(self):
        mapes, betas = [], []
        for beta in np.arange(0.0, 1, 0.05):
            col2idx = "name tracking_from tracking_to pv ev ac es".split()
            col2idx = {k: i for i, k in enumerate(col2idx)}
            n_actual_tps = len([x for x in self.sheetnames if "TP" in x])
            data = self.dfs["Tracking Overview"].values
            tracking_start_date = data[0, col2idx['tracking_from']]
            tracking_end_date = data[-1, col2idx['es']]
            PD = (tracking_end_date - tracking_start_date).days
            print(f"PD={PD}")
            n_expected_tps = PD / 20
            ats = [0]; ess = [0]; peacs = []
            tats = [PD/n_expected_tps]; tess = [PD/n_expected_tps]
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
            mapes.append(mape)
            betas.append(beta)
        best_beta = sorted(zip(betas, mapes), key=lambda x: x[1])[0][0]
        plt.title(f"Best Beta Value = {best_beta}")
        plt.xlabel("Beta")
        plt.ylabel("Mape Value")
        plt.plot(betas, mapes)
        plt.show()
        return best_beta

    def time_forecasting(self):

        figures, axes = plt.subplots(nrows=1, ncols=1)
        count=0
        row, col = 0, 0
        result = []
        for idx, datafile in enumerate(ReferenceClassTime.PROJECTS):
            super().__init__(datafile)
            beta = 0.05
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
                #print(f"TP {t} - pEAC={eac:.3f}")
                peacs.append(eac)
            print(f"Actual EAC {ats[-1]:.3f}")
            mape, error = self.MAPE([ats[-1]]*len(peacs[:-1]), peacs[:-1])
            print(f"mape={mape} error={error}")
            TPs = [str(x) for x, tp in enumerate(self.tracking_periods)]
            # axes[row][col].set_title(datafile + f" -- mape={mape: .3f}")
            # axes[row][col].set_ylabel("Mape Values")
            # if row==1 and col <= 1: axes[row][col].set_xlabel("Tracking Periods")
            axes.plot(TPs, np.append(error,0), label=f"{datafile} - mape={round(mape, 2)}")
            result.append((TPs, np.append(error,0), f"{datafile} - mape={round(mape, 2)}"))
            axes.set_title("K61-Reference Class")
            axes.legend()
            if (idx+1)%2 == 0: 
                row += 1; col=0
            else: col += 1
        plt.show()
        return result
        



            

    
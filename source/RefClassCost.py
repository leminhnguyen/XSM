import numpy as np
from matplotlib import pyplot as plt
import pandas

from XSM import XSM
from timefc import Time


class RefClassCost:

    PROJECTS = ["project2", "project3", "project4", "project5", "project6"]

    def __init__(self, datafile):
        self.df = pandas.read_excel(f'data/{datafile}.xlsx')
        self.BAC = list(self.df["PV"])[-1]
        self.num_actual_tps = len(self.df["AT"])
        self.num_expected_tps = len(self.df["AT"])
        self.datafile = datafile

    def MAPE(self, ytrue, ypred):
        ytrue = np.array(ytrue) 
        ypred = np.array(ypred)
        error = np.abs((ytrue-ypred)/ytrue) * 100
        mean_error = np.mean(error)
        return mean_error, error 

    def get_best_beta(self):
        mapes, betas = [], []
        for beta in np.arange(0.0, 1, 0.05):
            betas.append(beta)
            acs = [0]; evs = [0]; peacs = []
            tacs = [self.BAC/self.num_expected_tps]
            tevs = [self.BAC/self.num_expected_tps]
            for t in range(1, self.num_actual_tps+1):
                cost = self.df["AC"][t-1]
                acs.append(cost)
                tac = beta*(acs[t]-acs[t-1]) + (1-beta)*tacs[t-1]
                tacs.append(tac)

                ev = self.df["EV"][t-1]
                evs.append(ev)
                tev = beta*(evs[t]-evs[t-1]) + (1-beta)*tevs[t-1]
                #print(f"tev - {tev}")
                tevs.append(tev)

                k = (self.BAC-evs[t])/tev
                eac = acs[t] + k*tac
                peacs.append(eac)
            print(f"Actual EAC {acs[-1]:.3f}")
            mape, error = self.MAPE([list(self.df["AC"])[-1]]*len(peacs[:-1]), peacs[:-1])
            # print(f"mape={mape} error={error}")
            print(mape)
            print()
            mapes.append(mape)

        best_beta = sorted(zip(betas, mapes), key=lambda x: x[1])[0][0]
        plt.title(f"Best Beta Value = {best_beta}")
        plt.xlabel("Beta")
        plt.ylabel("Mape Value")
        plt.plot(betas, mapes)
        plt.show()


    def cost_forcast(self):
        figures, axes = plt.subplots(nrows=1, ncols=1)
        count=0
        row, col = 0, 0
        result = []
        mapes = []
        for idx, datafile in enumerate(RefClassCost.PROJECTS):
            self.__init__(datafile)
            beta = 0.00
            acs = [0]; evs = [0]; peacs = []
            tacs = [self.BAC/self.num_expected_tps]
            tevs = [self.BAC/self.num_expected_tps]
            start_test = False
            for t in range(1, self.num_actual_tps+1):
                cost = self.df["AC"][t-1]
                acs.append(cost)
                tac = beta*(acs[t]-acs[t-1]) + (1-beta)*tacs[t-1]
                tacs.append(tac)

                ev = self.df["EV"][t-1]
                evs.append(ev)
                tev = beta*(evs[t]-evs[t-1]) + (1-beta)*tevs[t-1]
                #print(f"tev - {tev}")
                tevs.append(tev)

                k = (self.BAC-evs[t])/tev
                eac = acs[t] + k*tac
                peacs.append(eac)
            print(f"Actual EAC {acs[-1]:.3f}")
            mape, error = self.MAPE([list(self.df["AC"])[-1]]*len(peacs[:-1]), peacs[:-1])
            # print(f"mape={mape} error={error}")
            print(mape)
            print()
            mapes.append(mape)
            TPs = [f"TP {_id}" for _id in range(self.num_actual_tps+1)]
            axes.plot(TPs[:-1], np.append(error,0), label=f"{datafile} - mape={round(mape, 2)}")
            result.append((TPs[:-1], np.append(error,0), f"{datafile} - mape={round(mape, 2)}"))
            axes.set_title("K61-Reference Class")
            axes.legend()
            if (idx+1)%2 == 0: 
                row += 1; col=0
            else: col += 1
        plt.show()
        return result


    

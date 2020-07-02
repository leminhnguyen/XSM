import sys
sys.path.append("source")

from matplotlib import pyplot as plt
import numpy as np

from cost import Cost
from cost_evm import CostEVM
from dynamic import DynamicCost
from timefc import Time
from RefClassTime import ReferenceClassTime
from RefClassCost import RefClassCost


if __name__ == "__main__":
    datafile = sys.argv[1]
   

    # dynamic forcasting
    # print("\n-------- Dynamic Forcasting ---------")
    # dynamicfocasting = DynamicCost(datafile)
    # dynamicfocasting.forecast()

    # # cost forcasting
    # print("\n-------- Cost Forcasting -----------")
    # costforcasting = Cost("C2013-12")
    # costforcasting.cost_forecasting()

    # costevm forcasting
    # print("\n------ Cost EVM Forcasting ----------")
    # evmforcasting = CostEVM(datafile)
    # evmforcasting.forecast()

    # reference class forcasting
    # print("\n--------- Time Forcasting -----------")
    # plt.style.use("seaborn")
    # row, col = 0, 0
    # PROJECTS = ["C2014-05", "C2014-06", "C2014-07", "C2014-08"]
    # prev = []
    # for idx, project in enumerate(PROJECTS):
    #     timeforcasting = Time(project)
    #     mape, error = timeforcasting.time_forecasting()
    #     TPs = [str(x) for x, tp in enumerate(timeforcasting.tracking_periods)]
    #     plt.plot(TPs, np.append(error,0), label=f"{project} - mape={round(mape, 2)}")
    #     plt.title("K60 - Dynamic Approach")
    #     plt.legend()
    #     if (idx+1)%2 == 0: 
    #         row += 1; col=0
    #     else: col += 1
    #     prev.append((TPs, np.append(error,0), f"{project} - mape={round(mape, 2)}"))

    # print("\nReference Class Forcasting")
    # PROJECTS = ["C2014-05", "C2014-06", "C2014-07", "C2014-08"]
    # rc = ReferenceClassTime(datafile)
    # res = rc.time_forecasting()

    # fig, ax = plt.subplots(nrows=2, ncols=2)
    # ax[0][0].set_title(f"Compare Results - {PROJECTS[0]}")
    # ax[0][0].plot(prev[0][0], prev[0][1], label="K60-Dynamic Approach")
    # ax[0][0].plot(res[0][0], res[0][1], label="K61 - Reference Class")

    # ax[0][1].set_title(f"Compare Result - {PROJECTS[1]}")
    # ax[0][1].plot(prev[1][0], prev[1][1], label="K60-Dynamic Approach")
    # ax[0][1].plot(res[1][0], res[1][1], label="K61 - Reference Class")

    # ax[1][0].set_title(f"Compare Result - {PROJECTS[2]}")
    # ax[1][0].plot(prev[2][0], prev[2][1], label="K60-Dynamic Approach")
    # ax[1][0].plot(res[2][0], res[2][1], label="K61 - Reference Class")

    # ax[1][1].set_title(f"Compare Result - {PROJECTS[3]}")
    # ax[1][1].plot(prev[3][0], prev[3][1], label="K60-Dynamic Approach")
    # ax[1][1].plot(res[3][0], res[3][1], label="K61 - Reference Class")

    # plt.legend()
    # plt.show()

    ref = RefClassCost(datafile=datafile)
    ref.cost_forcast()

    
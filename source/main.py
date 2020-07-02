import sys
sys.path.append("source")

from matplotlib import pyplot as plt
import numpy as np

from cost import Cost
from cost_evm import CostEVM
from dynamic import DynamicCost
from timefc import Time
from RefClassTime import ReferenceClassTime


if __name__ == "__main__":
    datafile = sys.argv[1]
    # time forcasting
    print("\n--------- Time Forcasting -----------")
    plt.style.use("seaborn")
    # figure, axes = plt.subplots(nrows=2, ncols=2)
    row, col = 0, 0
    PROJECTS = ["C2014-05", "C2014-06", "C2014-07", "C2014-08"]
    prev = []
    for idx, project in enumerate(PROJECTS):
        timeforcasting = Time(project)
        mape, error = timeforcasting.time_forecasting()
        TPs = [str(x) for x, tp in enumerate(timeforcasting.tracking_periods)]
        # axes[row][col].set_title(project + f" -- mape={mape: .3f}")
        # axes[row][col].set_ylabel("Mape Values")
        # if row==1 and col <= 1: axes[row][col].set_xlabel("Tracking Periods")
        plt.plot(TPs, np.append(error,0), label=f"{project} - mape={round(mape, 2)}")
        plt.legend()
        if (idx+1)%2 == 0: 
            row += 1; col=0
        else: col += 1
        prev.append((TPs, np.append(error,0), f"{project} - mape={round(mape, 2)}"))
        

    # plt.show()

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
    print("\nReference Class Forcasting")
    PROJECTS = ["C2014-05", "C2014-06", "C2014-07", "C2014-08"]
    # for project in PROJECTS:
    #     rc = ReferenceClassTime(project)
    #     rc.get_best_beta()
    rc = ReferenceClassTime(datafile)
    res = rc.time_forecasting()

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(prev[0][0], prev[0][1], label="K60")
    ax.plot(res[0][0], res[0][1], label="K61")
    ax.legend()
    plt.show()

    
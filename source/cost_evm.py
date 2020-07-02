from XSM import XSM

class CostEVM(XSM):

    def __init__(self, data_file):
        super().__init__(data_file)

    def forecast(self):
        EAC_costs = []; t=1
        for period in self.tracking_periods:
            print("Tracking Period: " + period)
            cols = self.find_column_indices(self.dfs[period].values[1], ["ID", "Actual Cost", "Earned Value (EV)", "Planned Value (PV)"])
            data = self.dfs[period].values[2:, cols]
            AC, EV, PV = data[0, 1:]
            CPI = EV/AC
            EAC = (self.BAC-EV)/CPI + AC
            print("Predict EAC:", EAC)
            EAC_costs.append(EAC)
        print("Project actual costs: ", data[0,1])
        mape, error = self.MAPE([AC]*len(EAC_costs[:-1]), EAC_costs[:-1])
        print("EVM MAPE: ", mape)
        return error, mape
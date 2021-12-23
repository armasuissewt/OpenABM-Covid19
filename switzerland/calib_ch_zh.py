"""
This code is based on "Example Multi-Strain with Vaccination"
written by roberthinch.

Calibrate Zürich.

Created: 23. Dec. 2021
Author: Adrian Schneider
"""

import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt

sys.path.append("../src/COVID19")
from model import VaccineSchedule, Model, Parameters
from strain import Strain
from vaccine import Vaccine


def relative_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), filename)

if __name__ == '__main__':

    collect_data = pd.DataFrame()

    for ir in [3.0, 5.0]:

        p = Parameters(
            input_param_file=relative_path("zh/baseline_parameters.csv"),
            output_file_dir=".",
            param_line_number=1,
            input_households=relative_path("zh/baseline_household_demographics.csv"),
            read_param_file=True
        )

        #p.set_param("n_total", 100000)
        p.set_param("infectious_rate", ir)
        p.set_param("sd_infectiousness_multiplier", 1.4)
        p.set_param("end_time", 120)

        abm = Model(p)

        print("Calibration Zürich: Number of agents " + str(p.get_param("n_total")) + ", infectious_rate " + str(p.get_param("infectious_rate")) + ", sd_infectiousness_multiplier " + str(p.get_param("sd_infectiousness_multiplier")))

        abm.run()

        dataName = str(p.get_param("infectious_rate"))+":"+str(p.get_param("sd_infectiousness_multiplier"))
        collect_data[dataName] = pd.DataFrame(abm.results, columns=['n_death'])["n_death"].diff()

    collect_data.to_csv("ch_zh_calib.csv")
    collect_data.plot()
    plt.show()

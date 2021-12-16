"""
This code is based on "Example Multi-Strain with Vaccination"
written by roberthinch.

Model of Kanton Zürich with rising Omikron

Created: 16. Dec. 2021
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

    p = Parameters(
        input_param_file=relative_path("zh/baseline_parameters.csv"),
        output_file_dir=".",
        param_line_number=1,
        input_households=relative_path("zh/baseline_household_demographics.csv"),
        read_param_file=True,
    )

    print("Model Zürich: Number of agents " + str(p.get_param("n_total")))

    abm = Model(p)

    for t in range(60):
        abm.one_time_step()

    timeseries = pd.DataFrame(abm.results, columns=['total_infected', 'total_death', 'n_recovered'])
    timeseries['n_newinfected'] = timeseries["total_infected"].diff()
    print(timeseries)
    timeseries.plot()
    plt.show()
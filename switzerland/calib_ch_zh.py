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

    # open public data - wave 20. Oct. 2021
    zh_data_cum_deaths = pd.read_csv('zh/public_data.csv', skiprows=list(range(1, 594)))['ncumul_deceased'].fillna(0)
    zh_data_cum_deaths = zh_data_cum_deaths.subtract(zh_data_cum_deaths[0])
    print(zh_data_cum_deaths)


    for mult in [1.5, 1.7]:
        for ir in [4.0, 4.5]:

            p = Parameters(
                input_param_file=relative_path("zh/baseline_parameters.csv"),
                output_file_dir=".",
                param_line_number=1,
                input_households=relative_path("zh/baseline_household_demographics.csv"),
                read_param_file=True
            )

            p.set_param("n_total", 100000)
            p.set_param("infectious_rate", ir)
            p.set_param("sd_infectiousness_multiplier", mult)
            p.set_param("end_time", 80)
            p.set_param("n_seed_infection", 100)

            abm = Model(p)

            print("Calibration Zürich: Number of agents " + str(p.get_param("n_total")) + ", infectious_rate " + str(p.get_param("infectious_rate")) + ", sd_infectiousness_multiplier " + str(p.get_param("sd_infectiousness_multiplier")))

            abm.run()

            collect_data = pd.DataFrame()
            collect_data['zh_obs'] = zh_data_cum_deaths
            dataName = str(p.get_param("infectious_rate"))+":"+str(p.get_param("sd_infectiousness_multiplier"))
            df_accum_daily_deaths =  pd.DataFrame(abm.results, columns=['n_death'])["n_death"]
            collect_data[dataName] = df_accum_daily_deaths

            collect_data.to_csv(dataName + ".csv")
            ax = collect_data.plot()
            fig = ax.get_figure()
            fig.savefig(dataName + ".pdf")





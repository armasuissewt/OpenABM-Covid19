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

    # open public data - wave Nov. 2021
    zh_data_cum_deaths = pd.read_csv('zh/public_data.csv', skiprows=list(range(1, 557)))['ncumul_deceased'].fillna(0)
    zh_data_cum_deaths = zh_data_cum_deaths.subtract(zh_data_cum_deaths[10])  # shift
    zh_data_cum_deaths = zh_data_cum_deaths.clip(lower=0)

    zh_data_cum_infected = pd.read_csv('zh/public_data.csv', skiprows=list(range(1, 557)))['ncumul_conf'].fillna(0)
    zh_data_cum_infected = zh_data_cum_infected.subtract(zh_data_cum_infected[10])  # shift
    zh_data_cum_infected = zh_data_cum_infected.clip(lower=0)

    p = Parameters(
        input_param_file=relative_path("zh/baseline_parameters.csv"),
        output_file_dir=".",
        param_line_number=1,
        input_households=relative_path("zh/baseline_household_demographics.csv"),
        read_param_file=True,
    )

    # Debug
    p.set_param("n_total", 1500000)

    print("Calibration Zürich: Number of agents " + str(p.get_param("n_total")) + ", infectious_rate " + str(p.get_param("infectious_rate")) +
          ", sd_infectiousness_multiplier " + str(p.get_param("sd_infectiousness_multiplier")) +
          ", n_seed_infections " + str(p.get_param("n_seed_infection")))


    abm = Model(p)

    for t in range(60):
        abm.one_time_step()

    # restrictions: 2G, 2G+, Homeoffice
    abm.update_running_params("relative_transmission_occupation", 0.9) # reduce work infections
    for t in range(120):
        abm.one_time_step()

    # print results
    dataName = str(p.get_param("infectious_rate")) + ":" + str(p.get_param("sd_infectiousness_multiplier"))

    collect_data_death = pd.DataFrame()
    collect_data_death['zh_deaths_observed'] = zh_data_cum_deaths
    collect_data_death[dataName] = pd.DataFrame(abm.results, columns=['n_death'])["n_death"]
    ax = collect_data_death.plot()
    fig = ax.get_figure()
    fig.savefig("sim-" + dataName + "-deaths" + ".pdf")

    collect_data_infected = pd.DataFrame()
    collect_data_infected['zh_infected_observed'] = zh_data_cum_infected
    collect_data_infected[dataName] = pd.DataFrame(abm.results, columns=['total_infected'])["total_infected"]
    collect_data_infected.to_csv(dataName + "-infected" + ".csv")
    ax = collect_data_infected.plot()
    fig = ax.get_figure()
    fig.savefig("sim-" + dataName + "-infected" + ".pdf")
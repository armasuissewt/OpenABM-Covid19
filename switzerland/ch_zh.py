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

sys.path.append("../src/COVID19")
from model import VaccineSchedule, Model
from strain import Strain
from vaccine import Vaccine
import matplotlib.pyplot as plt

if __name__ == '__main__':

    n_total = 152000 # run simulation with 10% of population

    params = {"n_total": n_total, "max_n_strains": 2}
    abm = Model(params=params)

    # add a new strain
    transmission_multiplier = 1.6;
    hospitalised_fraction = [0.001, 0.001, 0.01, 0.05, 0.05, 0.10, 0.15, 0.30, 0.5]

    strain_delta = abm.add_new_strain(
        transmission_multiplier=transmission_multiplier,
        hospitalised_fraction=hospitalised_fraction)

    # set cross-immunity between strains
    cross_immunity_mat = [
        [1.0, 0.8],
        [0.8, 1.0]
    ]
    abm.set_cross_immunity_matrix(cross_immunity_mat)

    # add vaccine
    full_efficacy_base = 0.6
    full_efficacy_delta = 0.3
    symptoms_efficacy_base = 0.85
    symptoms_efficacy_delta = 0.6
    severe_efficacy_base = 0.95
    severe_efficacy_delta = 0.90
    vaccine = abm.add_vaccine(
        full_efficacy=[full_efficacy_base, full_efficacy_delta],
        symptoms_efficacy=[symptoms_efficacy_base, symptoms_efficacy_delta],
        severe_efficacy=[severe_efficacy_base, severe_efficacy_delta],
        time_to_protect=14,
        vaccine_protection_period=365
    )

    # create a vaccine schedule
    schedule = VaccineSchedule(
        frac_0_9=0,
        frac_10_19=0,
        frac_20_29=0.02,
        frac_30_39=0.02,
        frac_40_49=0.02,
        frac_50_59=0.02,
        frac_60_69=0.02,
        frac_70_79=0.02,
        frac_80=0.02,
        vaccine=vaccine
    )

    # run the model for 30 time steps
    for t in range(30):
        abm.one_time_step()

    # add lockdown and start vaccination schedule
    abm.update_running_params("lockdown_on", True)

    # run the model for 70 time steps and vaccinate
    for t in range(70):
        abm.vaccinate_schedule(schedule)
        abm.one_time_step()

        # turn off lockdown and put in some social distancing (10% reduction in transmission rates outside), then run for 50 time steps
    abm.update_running_params("lockdown_on", False)
    abm.update_running_params("relative_transmission_occupation", 0.9)
    abm.update_running_params("relative_transmission_random", 0.9)
    for t in range(40):
        abm.one_time_step()

        # seed delta strain in 20 random people
    idx_seed = np.random.choice(n_total, 20, replace=False)
    for idx in range(len(idx_seed)):
        abm.seed_infect_by_idx(ID=idx_seed[idx], strain=strain_delta)

    # run the model for 50 more time steps
    for t in range(100):
        abm.one_time_step()

    results = abm.results
    results["new_infected"] = results["total_infected"].diff()
    df_res = results.loc[:, ["time", "new_infected", "hospital_admissions"]]

    print(df_res.to_numpy().astype(int))
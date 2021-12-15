"""
Example 101
Get the baseline parameters, model, run for a few time steps and print the output

Created: 17 April 2020
Author: roberthinch
"""

import COVID19.model as abm
import pandas as pd
import matplotlib.pyplot as plt

# get the model overiding a couple of params
model = abm.Model( params = { "n_total" : 15000})

# do nothing for 4 weeks
for t in range(28):
    model.one_time_step()

# lockdown for 2 weeks
model.update_running_params("lockdown_on", False)
for t in range(14):
    model.one_time_step()

# stop lockdown for the next 4 weeks
model.update_running_params("lockdown_on", False)
for t in range(28):
    model.one_time_step()

# print the basic output
print( model.results )

timeseries = pd.DataFrame( model.results, columns=['total_infected', 'total_death', 'n_recovered' ] )
timeseries['n_newinfected'] = timeseries["total_infected" ].diff()
timeseries.plot()
plt.show()



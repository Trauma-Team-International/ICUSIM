from icusim.icu_burden_simulator import simulate
from icusim.stats_to_dataframe import stats_to_dataframe
from icusim.params import params

out = simulate(params())
df = stats_to_dataframe(out)

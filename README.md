# ICU Burden Simulator
Intensive Care Unit (ICU) burden simulator for python.

### Logic

"""
- there is a certain number of patients at start day_total_cases
- each day there are more new patients based on doubles_in_days
- each day some patients will die based on case_fatality_rate
- each day some patients are released based on mean_duration
    - all patients that meet mean_duration and did not die are released
- some patients can be admitted based on current available capacity
    - such patients will be added to day_total_cases
- some patients may not be admittable due to lack of current capacity
    - such patients will die
"""

#### Use

```
from tqdm import tqdm

out = []

for i in tqdm(range(1000)):
    
    results = simulate(params())
    df = stats_to_dataframe(results)
    
    total_refused = df.standard_icu_total_refused + df.ventilated_icu_total_refused
    total_refused = sum((total_refused > 0).astype(int))
    
    round_out = df.max().tolist()
    
    out.append(round_out + [total_refused])
```
And
```
import pandas as pd

df = pd.DataFrame(out)
columns = stats_to_dataframe(simulate(params())).columns.tolist() + ['expired_because_refused']

df.columns = columns
```

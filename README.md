# ICU Burden Simulator
Intensive Care Unit (ICU) burden simulator for python.

### Benefits



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

- There is no progression; ventilation need is decided upon admission
- 


### Input Parameters

name | default | what is it?
--- | --- | --- 
`initial_patient_count` | 120 | number of patients to start with
`require_ventilation_rate` | 0.3 | percentage of patients requiring ventilation
`days_to_simulate` | 20 | number of days to simulate
`doubles_in_days` | 10 | the number of days it takes to double daily cases
`standard_icu_capacity` | 400 | capacity for standard ICU
`ventilated_icu_capacity` | 230 | capacity for ventilated ICU
`standard_icu_fatality_rate` | 0.4 | case fatality rate for standard ICU patients
`ventilated_icu_fatality_rate` | 0.8 | case fatality rate for ventilated ICU patients
`standard_icu_stay_duration` | 10 | mean duration of standard ICU stay
`ventilated_icu_stay_duration` | 10 | mean duration of ventilated ICU stay

Parameters can be generated randomly with the below function:
```
def params(show_params=False):
    
    import random
    import numpy as np
    
    _capacity_ = random.choice(list(range(200, 1000, 50)))
    _ventilated_capacity_ = (np.random.normal(1, 0.01) * .5)
    _fatality_rate_ = round(random.choice(np.arange(0.2, 0.6, .01)), 2)
    _ventilated_fatality_factor_ = random.choice(np.arange(1.3, 1.7, 0.01))
    
    _duration_ = random.choice(list(range(8, 25, 1)))
    _ventilated_duration_factor_ = random.choice(np.arange(1, 1.2, 0.01))
    
    p = {
         'initial_patient_count': 120,
         'require_ventilation_rate': round(random.choice(np.arange(.3, .8, .01)), 3),
         'days_to_simulate': 50,
         'doubles_in_days': round(random.choice(np.arange(2.0, 12.0, .1)), 2),
         'standard_icu_capacity': int(_capacity_ * (1 - _ventilated_capacity_)),
         'ventilated_icu_capacity': int(_capacity_ * _ventilated_capacity_),
         'standard_icu_fatality_rate': float(_fatality_rate_),
         'ventilated_icu_fatality_rate': round(_fatality_rate_ * (np.random.normal(1, 0.01) * _ventilated_fatality_factor_), 2),
         'standard_icu_stay_duration': int(_duration_),
         'ventilated_icu_stay_duration': int(_duration_ * (np.random.normal(1, 0.01) * _ventilated_duration_factor_)),
    }
    
    if show_params:
        for key in p.keys():
            print(key,p[key])
    
    return p
```

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

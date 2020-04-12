<h1 align="center">
  <br>
  <a href="http://autonom.io"><img src="https://raw.githubusercontent.com/autonomio/ICUSIM/master/logo.png" alt="ICUSIM" width="250"></a>
  <br>
</h1>

<h3 align="center">Intensive Care Unit Simulation</h3>

<p align="center">
  <a href="#what">what?</a> •
  <a href="#why">why?</a> •
  <a href="#how">how?</a> •
  <a href="#start-simulating">start simulating</a> •
  <a href="https://autonom.io">About Autonomio</a> •
  <a href="https://github.com/autonomio/ICUSIM/issues">Issues</a> •
  <a href="#License">License</a>
</p>
<hr>
<p align="center">
ICUSIM is a Monte Carlo simulator for understanding and forecasting the demand for Intensive Care Unit (ICU) and ventilation resources.
</p>

<hr>

### What?

ICUSIM dramatically simplifies the process ICU demand, capacity, and fatality simulation. The simulation is based on a logic that closely resembles the current empirical understanding of the problem. The power of Monte Carlo simulation can be summarized in two points: 

- Input parameter ranges are based on empirical evidence
- There is no ambiquity in terms of results

**Fig 1:** An example of simulation result where we test how often peak daily demand for standard ICU capacity stays below 278 (the official forecast of THL in Finland). 

<img src=https://media.discordapp.net/attachments/696359200774684745/698103055803220019/9jMw10xwcwAAAABJRU5ErkJggg.png>

This allows the consumer of the information to establish their own point-of-view regarding how likely a certain outcome may be. The Monte Carlo method entirely takes away doubt from the question "given a range of parameters, how often so and so values appear".

<hr>

### Why?

- Make forecasts to increased preparadness
- Test plausibility of forecasts made with other methods

<hr>

### How?

ICUSIM follows a straightforward logic:

- There is a certain number of patients to start with
- Patients are split between standard and ventilated ICU
- Patients can not move between standard and ventilated ICU
- New patients come in based on `doubles_in_days` input parameter
- As new patients come in, each is assigned with a probability to survive
- As new patients come in, each is assigned a stay duration
- Released or dead, it happens when stay duration is completed
- If there is less capacity than there is demand, patients will die accordingly

Outcomes are controlled through **Input Parameters**, which are provided separately for _standard ICU_ and _ventilated ICU_.

name | type | description
--- | --- | --- 
`initial_patient_count` | int | the number of patients to start with
`days_to_simulate` | int | number of days to simulate
`total_capacity_min` | int | minimum for total available capacity
`total_capacity_max` | int | maximum for total available capacity
`ventilated_icu_share_min` | float | minimum for ventilated capacity
`ventilated_icu_share_max` | float | maximum for ventilated capacity
`standard_cfr_min` | float | minimum case fatality rate for standard ICU
`standard_cfr_max` | float | maximum case fatality rate for standard ICU
`ventilated_cfr_min` | float | minimum case fatality rate for ventilated ICU
`ventilated_cfr_max` | float | maximum case fatality rate for ventilated ICU
`standard_duration_min` | float | minimum mean duration for standard ICU stay
`standard_duration_max` | float | maximum mean duration for standard ICU stay
`ventilated_duration_factor_min` | float | minimum ratio for ventilated capacity per standard standard 
`ventilated_duration_factor_max` | float | maximum ratio for ventilated capacity per standard standard 
`doubles_in_days_min` | float | minimum number of days it takes for exponental growth to happen 
`doubles_in_days_max` | float | maximum number of days it takes for eponental growth to happen
`ventilation_rate_min` | float | minimum rate at which ventilation is required
`ventilation_rate_max` | float | maximum rate at which ventilation is required
`show_params` | bool | prints out the parameters if True

<hr>

### 💾 Install

Released version:

#### `pip install icusim`

Daily development version:

#### `pip install git+https://github.com/autonomio/ICUSIM`

<hr>

### Start Simulating

The first step is to create a `params` function that handles randomly picking parameters and where the various parameter ranges are set. Make sure to follow parameter ranges that you can established with available empirical evidence. An fully functional example that is relevant for Finland is provided below. You can simply change the values to meet the evidence for the area/s of your interest.

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

Run a single simulation: 

```
import icusim

params = icusim.params()
icusim.simulate(params)
```

Run many simulations:

```
import icusim
import tqdm

out = []

for i in tqdm(range(1000)):
    
    results = simulate(params())
    df = stats_to_dataframe(results)
    
    round_out = df.max().tolist()
    
    out.appendround_out)
```
Get the results onto a dataframe:

```
import pandas as pd

df = pd.DataFrame(out)
columns = stats_to_dataframe(simulate(params())).columns.tolist()

df.columns = columns
```
Draw a histogram for analyzing the results:

```
astetik.hist(df, 'ventilated_icu_total_demand')
```
<hr>

### 💬 How to get Support

| I want to...                     | Go to...                                                  |
| -------------------------------- | ---------------------------------------------------------- |
| **...troubleshoot**           | [GitHub Issue Tracker]                   |
| **...report a bug**           | [GitHub Issue Tracker]                                     |
| **...suggest a new feature**  | [GitHub Issue Tracker]                                     |
| **...get support**            | [GitHub Issue Tracker]  · [Discord Chat]                         |
| **...have a discussion**      | [Discord Chat]                                            |

<hr>

### 📢 Citations

If you use ICUSIM for published work, please cite:

`Autonomio's ICUSIM [Computer software]. (2020). Retrieved from http://github.com/autonomio/ICUSIM.`

<hr>

### 📃 License

[MIT License](https://github.com/autonomio/talos/blob/master/LICENSE)

[github issue tracker]: https://github.com/automio/talos/issues
[discord chat]: https://discord.gg/55QDD9


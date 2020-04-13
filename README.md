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

- Make forecasts to increase preparadness
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

To run a simulation, you need two things:

- parameter dictionary
- `icusim.MonteCarlo()` command

Make sure to follow parameter ranges that you can established with available empirical evidence. A fully functional example that is relevant for Finland is provided below. You can simply change the values to meet the evidence for the area/s of your interest.

```
params = {'initial_patient_count': 80,
          'days_to_simulate': 50,
          'total_capacity_min': 200,
          'total_capacity_max': 1000,
          'ventilated_icu_share_min': .4,
          'ventilated_icu_share_max': .6,
          'standard_cfr_min': 0.2,
          'standard_cfr_max': 0.6,
          'ventilated_cfr_min': 1.3,
          'ventilated_cfr_max': 1.7,
          'standard_duration_min': 8.5,
          'standard_duration_max': 25.5,
          'ventilated_duration_factor_min': .9,
          'ventilated_duration_factor_max': 1.1,
          'doubles_in_days_min': 2.0,
          'doubles_in_days_max': 12.0,
          'ventilation_rate_min': 0.3,
          'ventilation_rate_max': 0.8}
```
Next you can start the simulation: 

```
import icusim
results = icusim.MonteCarlo(rounds=1000, params)
```

Access the results of the simulation: 

```
results.df
```

If you want to also perform **sensitivity analysis**: 

```
import icusim
results = icusim.SobolSensitivity(rounds=1000, params)
```

Once the rounds are completed, get the sensitivities: 

```
results.sensitivity('metric_name')
```


You can also run a single round simulation with **daily output**: 

```
import icusim

params = icusim.params()
icusim.simulate(params)
```

Draw a **histogram** for analyzing the results:

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


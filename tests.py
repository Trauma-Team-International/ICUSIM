import icusim

out = icusim.simulate(icusim.params())
df = icusim.stats_to_dataframe(out)

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

icusim.MonteCarlo(10, params)
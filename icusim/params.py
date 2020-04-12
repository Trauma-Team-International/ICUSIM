def params(initial_patient_count=120,
           days_to_simulate=50,
           total_capacity_min=200,
           total_capacity_max=1000,
           ventilated_icu_share_min=.4,
           ventilated_icu_share_max=.7,
           standard_cfr_min=.2,
           standard_cfr_max=.6,
           ventilated_cfr_min=1.3,
           ventilated_cfr_max=1.7,
           standard_duration_min=8,
           standard_duration_max=25,
           ventilated_duration_factor_min=1,
           ventilated_duration_factor_max=1.2,
           doubles_in_days_min=2.0,
           doubles_in_days_max=12.0,
           ventilation_rate_min=.3,
           ventilation_rate_max=.8,
           show_params=False):
    
    '''
    Creates input parameters for simulate().
    
    Below you have control over all the variable ranges, as 
    well as randomness properties. By default, uniform and 
    normal distributions are used, but you could use any 
    random functions you like.
    
    initial_patient_count | int | the number of patients to start with
    days_to_simulate | int | number of days to simulate
    total_capacity_min | int | minimum for total available capacity
    total_capacity_max | int | maximum for total available capacity
    ventilated_icu_share_min | float | minimum for ventilated capacity
    ventilated_icu_share_max | float | maximum for ventilated capacity
    standard_cfr_min | float | minimum case fatality rate for standard ICU
    standard_cfr_max | float | maximum case fatality rate for standard ICU
    ventilated_cfr_min | float | minimum case fatality rate for ventilated ICU
    ventilated_cfr_max | float | maximum case fatality rate for ventilated ICU
    standard_duration_min | float | minimum mean duration for standard ICU stay
    standard_duration_max | float | maximum mean duration for standard ICU stay
    ventilated_duration_factor_min | float | minimum ratio for ventilated capacity per standard standard 
    ventilated_duration_factor_max | float | maximum ratio for ventilated capacity per standard standard 
    doubles_in_days_min | float | minimum number of days it takes for exponental growth to happen 
    doubles_in_days_max | float | maximum number of days it takes for eponental growth to happen
    ventilation_rate_min | float | minimum rate at which ventilation is required
    ventilation_rate_max | float | maximum rate at which ventilation is required
    show_params | bool | prints out the parameters if True
    
    
    '''
    
    import random
    import numpy as np
    
    # change scale for stronger random effect (only applies to normally distributed)
    _random_normal_ = np.random.normal(loc=1, scale=0.01)
    
    # set max capacity 
    _capacity_ = random.choice(range(total_capacity_min, total_capacity_max, 50))
    
    # set the fraction of ventilation capacity
    _ventilated_capacity_ = random.choice(np.arange(ventilated_icu_share_min, ventilated_icu_share_max, step=.01))
    
    # set standard case fatality rate
    _fatality_rate_ = random.choice(np.arange(standard_cfr_min, standard_cfr_max, step=.01))
    
    # set ventilated case fatality rate
    _ventilated_fatality_factor_ = random.choice(np.arange(ventilated_cfr_min, ventilated_cfr_max, step=0.01))
    
    # set the mean duration of standard ICU stay (ventilated is based on it
    _standard_icu_stay_duration_ = random.choice(np.arange(standard_duration_min, standard_duration_max, step=0.1))
                       
    # set a multiplier for ventilated stay duration
    _temp_ = np.arange(ventilated_duration_factor_min, ventilated_duration_factor_max, step=0.01)                   
    _ventilated_duration_factor_ = random.choice(_temp_)
    
    # set the number of days during which doubling of cases happens
    _doubles_in_days_ = random.choice(np.arange(doubles_in_days_min, doubles_in_days_max, step=.1))
    
    # set the percent of patients that require ventilation
    _require_ventilation_rate_ = random.choice(np.arange(ventilation_rate_min, ventilation_rate_max, step=.01))
   
    # review the logic here
    doubles_in_days = _doubles_in_days_
    require_ventilation_rate = _require_ventilation_rate_
    standard_icu_capacity = _capacity_ * (1 - _ventilated_capacity_)
    ventilated_icu_capacity = _capacity_ * _ventilated_capacity_
    standard_icu_fatality_rate = _fatality_rate_
    ventilated_icu_fatality_rate = _fatality_rate_ * _random_normal_ * _ventilated_fatality_factor_
    standard_icu_stay_duration = _standard_icu_stay_duration_
    ventilated_icu_stay_duration = standard_icu_stay_duration * _random_normal_ * _ventilated_duration_factor_
    
    # generates the input parameters
    p = {'initial_patient_count': int(initial_patient_count),
         'days_to_simulate': int(days_to_simulate),
         'doubles_in_days': float(doubles_in_days),
         'ventilation_rate': float(require_ventilation_rate),
         'standard_capacity': int(standard_icu_capacity),
         'ventilated_capacity': int(ventilated_icu_capacity),
         'standard_cfr': float(standard_icu_fatality_rate),
         'ventilated_cfr': float(ventilated_icu_fatality_rate),
         'standard_duration': int(standard_icu_stay_duration),
         'ventilated_duration': int(ventilated_icu_stay_duration)}
    
    # print out the params
    if show_params:
        for key in p.keys():
            print(key, p[key])
    
    return p

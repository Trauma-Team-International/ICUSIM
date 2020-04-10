def params(initial_patient_count=120,
           days_to_simulate=50,
           capacity_min=200,
           capacity_max=1000,
           ventilated_icu_factor=.5,
           fatality_rate_min=.2,
           fatality_rate_max=.6,
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
    '''
    
    import random
    import numpy as np
    
    # change scale for stronger random effect (only applies to normally distributed)
    _random_normal_ = np.random.normal(loc=1, scale=0.01)
    
    # set max capacity 
    _capacity_ = random.choice(range(capacity_min, capacity_max, 50))
    
    # set the fraction of ventilation capacity
    _ventilated_capacity_ = (_random_normal_ * ventilated_icu_factor)
    
    # set standard case fatality rate
    _fatality_rate_ = random.choice(np.arange(fatality_rate_min, fatality_rate_max, step=.01))
    
    # set ventilated case fatality rate
    _ventilated_fatality_factor_ = random.choice(np.arange(ventilated_cfr_min, ventilated_cfr_max, step=0.01))
    
    # set the mean duration of standard ICU stay (ventilated is based on it
    _standard_icu_stay_duration_ = random.choice(range(standard_duration_min, standard_duration_max, 1))
                       
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
    p = {'initial_patient_count': initial_patient_count,
         'days_to_simulate': days_to_simulate,
         'doubles_in_days': doubles_in_days,
         'require_ventilation_rate': float(require_ventilation_rate),
         'standard_icu_capacity': int(standard_icu_capacity),
         'ventilated_icu_capacity': int(ventilated_icu_capacity),
         'standard_icu_fatality_rate': float(standard_icu_fatality_rate),
         'ventilated_icu_fatality_rate': float(ventilated_icu_fatality_rate),
         'standard_icu_stay_duration': int(standard_icu_stay_duration),
         'ventilated_icu_stay_duration': int(ventilated_icu_stay_duration)}
    
    # print out the params
    if show_params:
        for key in p.keys():
            print(key,p[key])
    
    return p

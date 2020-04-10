def params(show_params=False):
    
    '''
    Creates input parameters for simulate().
    
    Below you have control over all the variable ranges, as 
    well as randomness properties. By default, uniform and 
    normal distributions are used, but you could use any 
    random functions you like.
    '''
    
    import random
    import numpy as np
        
    initial_patient_count = 120
    days_to_simulate = 50
    
    _random_normal_ = (np.random.normal(1, 0.01)
    
    # set max capacity 
    _capacity_ = random.choice(list(range(200, 1000, 50)))
    
    # set the fraction of ventilation capacity
    _ventilated_capacity_ = (np.random.normal(1, 0.01) * .5)
    
    # set standard case fatality rate
    _fatality_rate_ = round(random.choice(np.arange(0.2, 0.6, .01)), 2)
    
    # set ventilated case fatality rate
    _ventilated_fatality_factor_ = random.choice(np.arange(1.3, 1.7, 0.01))
    
    # set a multiplier for ventilated stay duration
    _ventilated_duration_factor_ = random.choice(np.arange(1, 1.2, 0.01))
    
    # initialize values
    doubles_in_days = random.choice(np.arange(2.0, 12.0, .1))
    require_ventilation_rate = random.choice(np.arange(.3, .8, .01))
    standard_icu_capacity = _capacity_ * (1 - _ventilated_capacity_)
    ventilated_icu_capacity = _capacity_ * _ventilated_capacity_
    standard_icu_fatality_rate = _fatality_rate_
    ventilated_icu_fatality_rate = _fatality_rate_ * _random_normal_ * _ventilated_fatality_factor_
    standard_icu_stay_duration = int(random.choice(range(8, 25, 1)))
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

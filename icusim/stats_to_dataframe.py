=======


def stats_to_dataframe(results):

    import pandas as pd

    # pd.set_option("display.max_rows", 5)
    # pd.set_option("display.max_columns", 7)
    # pd.set_option('display.width', None)

    out = []
    cols = []

    # get day key
    for day in results.keys():

        _temp_ = []
        cols = []

        # get metric name key
        for metric in results[day].keys():

            _temp_.append(results[day][metric]['standard_icu'])
            _temp_.append(results[day][metric]['ventilated_icu'])

            cols.append('standard_icu_' + metric)
            cols.append('ventilated_icu_' + metric)

        out.append(_temp_)

    df = pd.DataFrame(out)
    df.columns = cols

    return df


def _dump_dictionary_(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                _dump_dictionary_(v)
            else:
                print('%s : %s' % (k, v))
    elif isinstance(obj, list):
        for v in obj:
            if hasattr(v, '__iter__'):
                _dump_dictionary_(v)
            else:
                print(v)
    else:
        print(obj)


def params(show_params=False):

    '''
    Creates input parameters for simulate().
    '''

    import random
    import numpy as np

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
    initial_patient_count = 120
    days_to_simulate = 50
    doubles_in_days = round(random.choice(np.arange(2.0, 12.0, .1)), 2)
    require_ventilation_rate = round(random.choice(np.arange(.3, .8, .01)), 3)
    standard_icu_capacity = int(_capacity_ * (1 - _ventilated_capacity_))
    ventilated_icu_capacity = int(_capacity_ * _ventilated_capacity_)
    standard_icu_fatality_rate = float(_fatality_rate_)
    ventilated_icu_fatality_rate = round(_fatality_rate_ * (np.random.normal(1, 0.01) * _ventilated_fatality_factor_), 2)
    standard_icu_stay_duration = int(random.choice(list(range(8, 25, 1))))
    ventilated_icu_stay_duration = int(standard_icu_stay_duration * (np.random.normal(1, 0.01) * _ventilated_duration_factor_))

    # generates the input parameters
    p = {'initial_patient_count': initial_patient_count,
         'days_to_simulate': days_to_simulate,
         'doubles_in_days': doubles_in_days,
         'require_ventilation_rate': require_ventilation_rate,
         'standard_icu_capacity': standard_icu_capacity,
         'ventilated_icu_capacity': ventilated_icu_capacity,
         'standard_icu_fatality_rate': standard_icu_fatality_rate,
         'ventilated_icu_fatality_rate': ventilated_icu_fatality_rate,
         'standard_icu_stay_duration': standard_icu_stay_duration,
         'ventilated_icu_stay_duration': ventilated_icu_stay_duration}

    # print out the params
    if show_params:
        for key in p.keys():
            print(key, p[key])

    return p


stats_to_dataframe(simulate(params()))
>>>>>>> master

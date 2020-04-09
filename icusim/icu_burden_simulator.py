"""
Scenario:
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

import collections
import random
import math
from enum import Enum

import simpy
import numpy as np


class Hospital:

    def __init__(self,
                 hospital_resource_manager,
                 departments,
                 departments_capacity,
                 require_ventilation_rate,
                 daily_refused_total,
                 daily_accepted_total,
                 daily_released_total,
                 daily_died_total,
                 statistic,
                 icu_properties):

        self.hospital_resource_manager = hospital_resource_manager
        self.departments = departments
        self.departments_capacity = departments_capacity
        self.require_ventilation_rate = require_ventilation_rate
        self.daily_refused_total = daily_refused_total
        self.daily_accepted_total = daily_accepted_total
        self.daily_released_total = daily_released_total
        self.daily_died_total = daily_died_total
        self.statistic = statistic
        self.icu_properties = icu_properties


class ICU_Types(Enum):
    standard_icu = 1
    ventilated_icu = 2


class ICU(object):
    def __init__(self,
                 icu_type: ICU_Types,
                 stay_duration: float,
                 fatality_probability: float):
        self.icu_type = icu_type
        self.stay_duration = stay_duration
        self.fatality_probability = fatality_probability


def hospital_manager(env,
                     icu_type,
                     hospital,
                     hours_in_day):
    """A hospital_manager tries to place each patient while there exists free
    space.
    """

    with hospital.hospital_resource_manager.request() as my_turn:
        # Wait until its our turn
        result = yield my_turn

        capacity = hospital.departments_capacity[icu_type]['capacity']
        new_cases = len(hospital.departments_capacity[icu_type]['icu_list'])
        place_available = capacity - new_cases

        # Check if it's our turn or if icu_type is filled in
        if place_available <= 0:
            hospital.daily_refused_total[icu_type] += 1

        else:
            # Hold a place
            _a_ = [1] * int(hospital.icu_properties[icu_type]['fatality_rate'] * 100)
            _b_ = [0] * int((1 - hospital.icu_properties[icu_type]['fatality_rate']) * 100)
            dist = _a_ + _b_
            patient_die = random.choice(dist)
            out_time = abs(np.random.normal(0, env.now + hospital.icu_properties[icu_type]['stay_duration']))
            icu = ICU(icu_type, out_time, patient_die)

            hospital.daily_accepted_total[icu_type] += 1
            hospital.departments_capacity[icu_type]['icu_list'].append(icu)

        yield env.exit()


def update_statistic(env,
                     hospital,
                     hours_in_day):
    # there should be +1 because simpy starts counting from 0
    nearest_hour = round(env.now+1)
    day_number = int(nearest_hour / hours_in_day)
    _a_ = nearest_hour != 0
    _b_ = nearest_hour % hours_in_day == 0
    _c_ = day_number not in hospital.statistic
    if _a_ and _b_ and _c_:
        standard_name = ICU_Types.standard_icu.name
        ventilated_name = ICU_Types.ventilated_icu.name

        total_died_refused_ventilated_icu = hospital.daily_refused_total[ventilated_name]
        total_demand = {icu_type: (hospital.daily_refused_total[icu_type] + hospital.daily_accepted_total[icu_type]) for icu_type in hospital.departments}
        total_released = {icu_type: hospital.daily_released_total[icu_type] for icu_type in hospital.departments}
        total_refused = {icu_type: hospital.daily_refused_total[icu_type] for icu_type in hospital.departments}
        _total_ventilated_died_ = hospital.daily_died_total[ventilated_name] + total_died_refused_ventilated_icu
        _total_standard_died_ = hospital.daily_died_total[standard_name]
        total_died = {standard_name: _total_standard_died_, ventilated_name: _total_ventilated_died_}

        hospital.statistic.update({day_number: {
            'total_demand': total_demand,
            'total_released': total_released,
            'total_refused': total_refused,
            'total_died': total_died
        }})

        # cleanup count for the next day
        hospital.daily_died_total.update({icu_type: 0 for icu_type in hospital.departments})

        hospital.daily_refused_total.update({icu_type: 0 for icu_type in hospital.departments})

        hospital.daily_released_total.update({icu_type: 0 for icu_type in hospital.departments})

        hospital.daily_accepted_total.update({icu_type: 0 for icu_type in hospital.departments})

    yield env.exit()


def update_icu_departments(env,
                           hospital,
                           update_frequency_in_hours):

    nearest_hour = round(env.now)

    if ((nearest_hour != 0) and (nearest_hour % update_frequency_in_hours == 0)):
        standard_name = ICU_Types.standard_icu.name
        ventilated_name = ICU_Types.ventilated_icu.name

        # apply fatality probability to standard icu
        standard_icu_list = hospital.departments_capacity[standard_name]['icu_list']
        standard_icu_die_list = filter_icu_list_by_fatality_probability(standard_icu_list, env.now)
        hospital.departments_capacity[standard_name]['icu_list'] = lists_diff(standard_icu_list, standard_icu_die_list)
        total_died_standard_icu = len(standard_icu_list) - len(hospital.departments_capacity[standard_name]['icu_list'])
        hospital.daily_died_total[standard_name] += total_died_standard_icu

        # apply fatality probability to ventilated icu
        ventilated_icu_list = hospital.departments_capacity[ventilated_name]['icu_list']
        ventilated_icu_die_list = filter_icu_list_by_fatality_probability(ventilated_icu_list, env.now)
        hospital.departments_capacity[ventilated_name]['icu_list'] = lists_diff(ventilated_icu_list, ventilated_icu_die_list)
        total_died_ventilated_icu = len(ventilated_icu_list) - len(hospital.departments_capacity[ventilated_name]['icu_list'])
        hospital.daily_died_total[ventilated_name] += total_died_ventilated_icu

        # release standard icu
        standard_icu_list = hospital.departments_capacity[standard_name]['icu_list']
        hospital.departments_capacity[standard_name]['icu_list'] = filter_icu_list_by_stay_duration(standard_icu_list, env.now)
        standard_icu_released_count = len(standard_icu_list) - len(hospital.departments_capacity[standard_name]['icu_list'])
        hospital.daily_released_total[standard_name] += standard_icu_released_count

        # release ventilated icu
        ventilated_icu_list = hospital.departments_capacity[ventilated_name]['icu_list']
        hospital.departments_capacity[ventilated_name]['icu_list'] = filter_icu_list_by_stay_duration(ventilated_icu_list, env.now)
        ventilated_icu_released_count = len(ventilated_icu_list) - len(hospital.departments_capacity[ventilated_name]['icu_list'])
        hospital.daily_released_total[ventilated_name] += ventilated_icu_released_count

    yield env.exit()


def patients_arrivals(env,
                      hospital,
                      hours_in_day,
                      patients_amount,
                      doubles_in_days,
                      update_frequency_in_hours):
    """Emulating patient arriving"""
    update_timeout = 1
    while True:

        total_population = get_population_by_day(env.now,
                                                 hours_in_day,
                                                 patients_amount,
                                                 doubles_in_days)
        # mean of hours and standard deviation of hours
        mu, sigma = (env.now + 13), 4
        require_ventilation_rate = hospital.require_ventilation_rate + np.random.normal(0, 0.01)
        total_standard_icu_population = round(total_population * (1 - require_ventilation_rate))
        total_ventilated_icu_population = round(total_population * require_ventilation_rate)
        arriving_standard_icu_distribution = np.random.normal(mu,
                                                              sigma,
                                                              int(total_standard_icu_population))
        arriving_ventilated_icu_distribution = np.random.normal(mu,
                                                                sigma,
                                                                int(total_ventilated_icu_population))
        standard_icu_name = hospital.departments[0]
        ventilated_icu_name = hospital.departments[1]
        total_icu_arriving_distribution = list(
            list(map(lambda ad: {
                'icu_type': standard_icu_name,
                'arriving_date': ad}, arriving_standard_icu_distribution))
            +
            list(map(lambda ad: {
                'icu_type': ventilated_icu_name,
                'arriving_date': ad}, arriving_ventilated_icu_distribution)))

        for hour in range(1, 25):
            filtered_icu_entities = list(filter(
                lambda icu_entity: (env.now <= icu_entity['arriving_date'] <= env.now + update_timeout),
                total_icu_arriving_distribution))

            for icu_entity in filtered_icu_entities:
                env.process(hospital_manager(env,
                                             icu_entity['icu_type'],
                                             hospital,
                                             hours_in_day))
                env.process(update_icu_departments(env,
                                                   hospital,
                                                   update_frequency_in_hours))

            if env.now != 0 and hour % hours_in_day == 0:
                env.process(update_statistic(env,
                                             hospital,
                                             hours_in_day))

            yield env.timeout(update_timeout)


def filter_icu_list_by_fatality_probability(icu_list, date_now):
    return list(
        filter(
            lambda icu: icu.stay_duration <= date_now and icu.fatality_probability,
            icu_list))


def filter_icu_list_by_stay_duration(icu_list, date_now):
    return list(
        filter(
            lambda icu: icu.stay_duration > date_now,
            icu_list))


def is_there_difference_between_max_and_current(departments_capacity):
    return departments_capacity['capacity'] - len(departments_capacity['icu_list'])


def get_nearest_day(time_now, hours_in_day):
    return math.ceil(time_now / hours_in_day)


def lists_diff(first, second):
    return [item for item in first if item not in set(second)]


def get_population_by_day(time_now,
                          hours_in_day,
                          patients_amount,
                          doubles_in_days) -> float:
    return (((get_nearest_day(time_now, hours_in_day)/doubles_in_days) * patients_amount) + patients_amount)


def get_daily_incoming_rate(hours_in_day, population) -> float:
    return hours_in_day / population


def generate_random_icu_list(icu_count: int,
                             icu_stay_duration: int,
                             icu_type: str,
                             hours_in_day: int) -> list:
    return list(
        map(
            lambda stay_duration: ICU(icu_type, round(stay_duration), np.random.choice(2, 1)[0]),
            np.random.normal(icu_stay_duration, hours_in_day*2, icu_count)))


def simulate(p: dict = {
             'initial_patient_count':  120,
             'require_ventilation_rate':  0.3,
             'days_to_simulate':  20,
             'doubles_in_days': 10,
             'standard_icu_capacity': 400,
             'ventilated_icu_capacity': 230,
             'standard_icu_fatality_rate': 0.4,
             'ventilated_icu_fatality_rate': 0.8,
             'standard_icu_stay_duration': 10,
             'ventilated_icu_stay_duration': 10},
             random_seed=None):

    starting_standard_icu_count = int(p['initial_patient_count'] * (1 - p['require_ventilation_rate']))
    starting_ventilated_icu_count = int(p['initial_patient_count'] * p['require_ventilation_rate'])

    _a_ = starting_standard_icu_count > p['standard_icu_capacity']
    _b_ = starting_ventilated_icu_count > p['ventilated_icu_capacity']

    if (_a_ or _b_):
        raise Exception("Starting amount can't be bigger then capacity!")

    hours_in_day = 24
    update_frequency_in_hours = 1

    hours_to_simulate = p['days_to_simulate'] * hours_in_day
    standard_icu_stay_duration = p['standard_icu_stay_duration'] * hours_in_day
    ventilated_icu_stay_duration = p['ventilated_icu_stay_duration'] * hours_in_day

    if random_seed is not None:
        random.seed(random_seed)

    # init stuff
    env = simpy.Environment()
    hospital_resource_manager = simpy.Resource(env, capacity=1)
    statistic = {}
    departments = [ICU_Types.standard_icu.name, ICU_Types.ventilated_icu.name]

    _temp_standard_icu_list_ = generate_random_icu_list(starting_standard_icu_count,
                                                        p['standard_icu_stay_duration'],
                                                        ICU_Types.standard_icu.name,
                                                        hours_in_day)

    _temp_ventilated_icu_list_ = generate_random_icu_list(starting_ventilated_icu_count,
                                                          p['ventilated_icu_stay_duration'],
                                                          ICU_Types.ventilated_icu.name,
                                                          hours_in_day)

    _temp_standard_icu_dict_ = {'capacity': p['standard_icu_capacity'], 'icu_list': _temp_standard_icu_list_}
    _temp_ventilated_icu_dict_ = {'capacity': p['ventilated_icu_capacity'], 'icu_list': _temp_ventilated_icu_list_}

    departments_capacity = {ICU_Types.standard_icu.name: _temp_standard_icu_dict_,
                            ICU_Types.ventilated_icu.name: _temp_ventilated_icu_dict_}

    _temp_standard_icu_meta_ = {'fatality_rate': p['standard_icu_fatality_rate'],
                                'stay_duration': p['standard_icu_stay_duration']}

    _temp_ventilated_icu_meta_ = {'fatality_rate': p['ventilated_icu_fatality_rate'],
                                  'stay_duration': p['ventilated_icu_stay_duration']}

    icu_properties = {ICU_Types.standard_icu.name: _temp_standard_icu_meta_,
                      ICU_Types.ventilated_icu.name: _temp_ventilated_icu_meta_}

    daily_released_total = {icu_type: 0 for icu_type in departments}
    daily_refused_total = {icu_type: 0 for icu_type in departments}
    daily_accepted_total = {icu_type: 0 for icu_type in departments}
    daily_died_total = {icu_type: 0 for icu_type in departments}

    hospital = Hospital(hospital_resource_manager,
                        departments,
                        departments_capacity,
                        p['require_ventilation_rate'],
                        daily_refused_total,
                        daily_accepted_total,
                        daily_released_total,
                        daily_died_total,
                        statistic,
                        icu_properties)

    # start simulation
    _temp_patients_arrival_ = patients_arrivals(env,
                                                hospital,
                                                hours_in_day,
                                                p['initial_patient_count'],
                                                p['doubles_in_days'],
                                                update_frequency_in_hours)

    env.process(_temp_patients_arrival_)
    env.run(until=hours_to_simulate)

    return hospital.statistic


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
            print(key,p[key])
    
    return p

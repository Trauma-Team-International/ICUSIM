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
            out_time = abs(np.random.normal(env.now, hospital.icu_properties[icu_type]['stay_duration']))
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

            if env.now != 0 and hour % hours_in_day == 0:
                env.process(update_icu_departments(env,
                                                   hospital,
                                                   update_frequency_in_hours))
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
             'ventilation_rate':  0.3,
             'days_to_simulate':  20,
             'doubles_in_days': 10,
             'standard_capacity': 400,
             'ventilated_capacity': 230,
             'standard_cfr': 0.4,
             'ventilated_cfr': 0.8,
             'standard_duration': 10,
             'ventilated_duration': 10},
             random_seed=None):

    starting_standard_icu_count = int(p['initial_patient_count'] * (1 - p['ventilation_rate']))
    starting_ventilated_icu_count = int(p['initial_patient_count'] * p['ventilation_rate'])

    _a_ = starting_standard_icu_count > p['standard_capacity']
    _b_ = starting_ventilated_icu_count > p['ventilated_capacity']

    if (_a_ or _b_):
        raise Exception("Starting amount can't be bigger then capacity!")

    hours_in_day = 24
    update_frequency_in_hours = 1

    hours_to_simulate = p['days_to_simulate'] * hours_in_day
    standard_icu_stay_duration = p['standard_duration'] * hours_in_day
    ventilated_icu_stay_duration = p['ventilated_duration'] * hours_in_day

    if random_seed is not None:
        random.seed(random_seed)

    # init stuff
    env = simpy.Environment()
    hospital_resource_manager = simpy.Resource(env, capacity=1)
    statistic = {}
    departments = [ICU_Types.standard_icu.name, ICU_Types.ventilated_icu.name]

    _temp_standard_icu_list_ = generate_random_icu_list(starting_standard_icu_count,
                                                        p['standard_duration'],
                                                        ICU_Types.standard_icu.name,
                                                        hours_in_day)

    _temp_ventilated_icu_list_ = generate_random_icu_list(starting_ventilated_icu_count,
                                                          p['ventilated_duration'],
                                                          ICU_Types.ventilated_icu.name,
                                                          hours_in_day)

    _temp_standard_icu_dict_ = {'capacity': p['standard_capacity'], 'icu_list': _temp_standard_icu_list_}
    _temp_ventilated_icu_dict_ = {'capacity': p['ventilated_capacity'], 'icu_list': _temp_ventilated_icu_list_}

    departments_capacity = {ICU_Types.standard_icu.name: _temp_standard_icu_dict_,
                            ICU_Types.ventilated_icu.name: _temp_ventilated_icu_dict_}

    _temp_standard_icu_meta_ = {'fatality_rate': p['standard_cfr'],
                                'stay_duration': standard_icu_stay_duration}

    _temp_ventilated_icu_meta_ = {'fatality_rate': p['ventilated_cfr'],
                                  'stay_duration': ventilated_icu_stay_duration}

    icu_properties = {ICU_Types.standard_icu.name: _temp_standard_icu_meta_,
                      ICU_Types.ventilated_icu.name: _temp_ventilated_icu_meta_}

    daily_released_total = {icu_type: 0 for icu_type in departments}
    daily_refused_total = {icu_type: 0 for icu_type in departments}
    daily_accepted_total = {icu_type: 0 for icu_type in departments}
    daily_died_total = {icu_type: 0 for icu_type in departments}

    hospital = Hospital(hospital_resource_manager,
                        departments,
                        departments_capacity,
                        p['ventilation_rate'],
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

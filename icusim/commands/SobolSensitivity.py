class SobolSensitivity:
    
    def __init__(self, rounds, param_dict):
             
        '''Sobol Sensitivity analysis where Saltelli sampling is 
        first performed to get the parameter combinations.

        Returns and object that contains the sensitivity analysis
        capability (self.sensitivity('')) and a dataframe with 
        simulation results (self.df). 
        
        rounds | int | number of times the simulation will be run
        param_dict | dict | dictionary with the input parameters
        
        '''

        self._rounds = rounds
        self._params = param_dict
        self._initial_patient_count = param_dict['initial_patient_count']
        self._days_to_simulate = param_dict['days_to_simulate']
        self._null = self._load_params()
        self._null = self._run()
        self._null = self._dataframe()

        del self.out
        
    def _load_params(self):
        
        out = {}

        # convert to salib problem format
        for key in self._params.keys():

            # the below assumes that min is always before max
            if 'min' in key:
                out[key[:-4]] = [self._params[key]]

            elif 'max' in key:
                out[key[:-4]] += [self._params[key]]

        # define the problem for sampling
        self.problem = {}
        self.problem['num_vars'] = len(out.keys())
        self.problem['names'] = list(out.keys())
        self.problem['bounds'] = [out[i] for i in out]

        # generate samples
        from SALib.sample import saltelli

        # this required by the sampling method (?!)

        _remnant_ = self._rounds % 8
        _sample_size_ = int((self._rounds - _remnant_) / 8)

        # draw the sample
        param_values = saltelli.sample(self.problem, _sample_size_, calc_second_order=False)

        self._params_ = []
        _temp_dict_ = {}

        for i in range(len(param_values)):
            
            self._labels = []
            _temp_dict_ = {}
            _temp_dict_['initial_patient_count'] = self._initial_patient_count
            _temp_dict_['days_to_simulate'] = self._days_to_simulate
            
            for ii, key in enumerate(list(out.keys())):

                _temp_dict_[key] = param_values[i][ii]
            
            _standard_capacity_ = _temp_dict_['total_capacity'] * _temp_dict_['ventilated_icu_share']
            
            _temp_dict_['standard_capacity'] = _standard_capacity_
            _temp_dict_['ventilated_capacity'] = _temp_dict_['total_capacity'] - _standard_capacity_
            _temp_dict_['ventilated_duration'] = _temp_dict_['standard_duration'] * _temp_dict_['ventilated_duration_factor']
            
            self._params_.append(_temp_dict_)

        return 0
                
    def _run(self):
    
        import icusim
        from tqdm import tqdm
        import pandas as pd

        self.out = []

        for i in tqdm(range(self._rounds)):

            results = icusim.simulate(self._params_[i])
            df = icusim.stats_to_dataframe(results)
            self.out.append(df.max().tolist())

        return 0

    def _dataframe(self):
        
        import pandas as pd
        import icusim
    
        self.results = pd.DataFrame(self.out)
        self.results.columns = icusim.columns()

        return 0
        
    def sensitivity(self, metric='standard_icu_total_demand'):
        
        '''Returns sensitivity analysis results for a given outcome.'''
        
        from SALib.analyze import sobol
        import pandas as pd
        
        Si = sobol.analyze(self.problem,
                           self.results[metric].values,
                           calc_second_order=False)
        
        _temp_ = {'first_order_sensitivity': Si['S1'], 'confidence': Si['S1_conf']}
        out = pd.DataFrame(_temp_, index=self.problem['names'])
        
        return out

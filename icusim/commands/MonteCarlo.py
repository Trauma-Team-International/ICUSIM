class MonteCarlo:
    
    def __init__(self, rounds, param_dict):
        
        '''Monte Carlo method for multi-round simulations.
        Returns and object that contains a dataframe with 
        simulation results (self.df).
        
        rounds | int | number of times the simulation will be run
        param_dict | dict | dictionary with the input parameters
        
        '''

        self.rounds = rounds
        self.params = param_dict
        self._null = self.run()
        self._null = self.dataframe()

    def load_params(self):
        
        import icusim
    
        return icusim.params(**self.params)
    
    
    def run(self):
    
        import icusim
        from tqdm import tqdm
        import pandas as pd

        self.out = []

        for i in tqdm(range(self.rounds)):

            results = icusim.simulate(self.load_params())
            df = icusim.stats_to_dataframe(results)
            self.out.append(df.max().tolist())

        return 0
            
    def dataframe(self):
        
        import pandas as pd
        import icusim
    
        self.df = pd.DataFrame(self.out)
        self.df.columns = icusim.columns()

        return 0

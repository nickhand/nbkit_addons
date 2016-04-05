#! /usr/bin/env python

import argparse
import logging
import sys
import yaml

from mpi4py import MPI

from nbodykit.extensionpoints import algorithms, Algorithm, DataSource
from nbodykit.utils.parallel import MPIPool

# setup the logging
comm = MPI.COMM_WORLD
rank = MPI.COMM_WORLD.rank
name = MPI.Get_processor_name()
logging.basicConfig(level=logging.INFO,
                    format='rank %d on %s: '%(rank,name) + \
                            '%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')


class BianchiWrapper(object):

    def __init__(self, template):
        
        with open(template, 'r') as ff:
            self.config = ff.read()
            
            raw_config = yaml.load(self.config)
            self.data_params = raw_config['input']['data']
            self.output = raw_config['output']
            
        self.algorithm = None

    def __call__(self, i, box):
        
        # have to create the algorithm
        if self.algorithm is None:
            
            # update the config file replace `box` keyword
            config = self.config.format(box=box)
            
            # parse the config file
            params, extra = Algorithm.parse_known_yaml('BianchiFFTPower', config)
            
            # initialize the algorithm
            self.algorithm = algorithms.BianchiFFTPower(**vars(params))
            
        else:
            
            # create a new ``data`` DataSource and set it
            kws = self.data_params.copy()
            kws['path'] = kws['path'].format(box=box)
            data = DataSource.from_config(kws)
            self.algorithm.input.update_data(data)
            
        result = self.algorithm.run()    
        output = self.output.format(box=box)
        self.algorithm.save(output, result)
            

def main(ns):

    # compute the tasks
    boxes = list(range(ns.start, ns.stop, ns.step))
    
    # initialize the algorithm wrapper
    bianchi = BianchiWrapper(ns.config)
    
    # initialize the worker pool
    kws = {'comm':comm, 'use_all_cpus':ns.use_all_cpus, 'debug':ns.debug}
    pool = MPIPool(bianchi, ns.N, **kws)
       
    # do the work
    results = pool.compute(boxes)
    

if __name__ == '__main__' :
    
    # parse
    desc = "run the ``BianchiFFTPower`` in batch mode, iterating over data boxes"
    parser = argparse.ArgumentParser(description=desc) 
    
    
    # the number of independent workers
    h = "the number of cpus per indepent worker"
    parser.add_argument('N', type=int, help=h)

    # start box number
    h = 'the data box number to start at'
    parser.add_argument('--start', type=int, help=h, required=True)
    
    # stop box number
    h = 'the data box number to stop at'
    parser.add_argument('--stop', type=int, help=h, required=True)
    
    # box iteration step
    h = 'the iteration step'
    parser.add_argument('--step', type=int, default=1, help=h)

    # the template config file
    parser.add_argument('-c', '--config', type=str, help=h, required=True)
        
    h = "set the logging output to debug, with lots more info printed"
    parser.add_argument('--debug', action="store_true", help=h)
                        
    h = "if `True`, include all available cpus in the worker pool"
    parser.add_argument('--use_all_cpus', action='store_true', help=h)
    
    ns = parser.parse_args()
    
    main(ns)
    
    
    
    

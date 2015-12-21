"""
    meanpower.py
    designed to read in a set of 1D/2D power plain text
    files and output the mean power to a plain text file
"""
import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import argparse as ap
from glob import glob
from nbodykit import files, dataset
import numpy
from lsskit.specksis import io

desc = "designed to read in a set of 1D or 2D power plain text " + \
       "files and output the mean power to a plain text file"
parser = ap.ArgumentParser(description=desc, 
                            formatter_class=ap.ArgumentDefaultsHelpFormatter)
                            
h = 'the mode, either 1D or 2D'
parser.add_argument('mode', choices=['1d', '2d'], help=h)
h = 'the pattern to match files power files on'
parser.add_argument('pattern', type=str, help=h)
h = 'the name of the output file'
parser.add_argument('output', default=None, type=str, help=h)
h = 'loop over these arguments, doing a string replace on the ' + \
    'input/output files, using %s format'
parser.add_argument('--batch', nargs='+', type=str, help=h)

args = parser.parse_args()


def average(datasets, weights=None, sum_only=[]):

    # check columns for all objects
    columns = [d.variables for d in datasets]
    if not all(sorted(cols) == sorted(columns[0]) for cols in columns):
        raise ValueError("cannot average DataSet with different column names")
        
    # compute the weights
    if weights is None:
        weights = numpy.ones((len(datasets),) + datasets[0].shape)
    else:
        if isinstance(weights, basestring):
            if weights not in columns[0]:
                raise ValueError("Cannot weight by `%s`; no such column" %weights)
            weights = numpy.array([d[weights] for d in datasets])
    
    # return a copy
    toret = datasets[0].copy()
    
    # take the mean or the sum   
    for name in columns[0]:
        col_data = numpy.array([d[name] for d in datasets])
        if name not in sum_only:
            with numpy.errstate(invalid='ignore'):
                toret[name] = (col_data*weights).sum(axis=0) / weights.sum(axis=0)
        else:
            toret[name] = numpy.sum(col_data, axis=0)
        
    # handle the metadata
    for key in datasets[0].attrs:
        try:
            toret.attrs[key] = numpy.mean([d.attrs[key] for d in datasets])
        except:
            pass
    
    
    return toret
        

def main():

    nbatch = 1
    if args.batch is not None:
        nbatch = len(args.batch)
    
    # do each pattern provided
    for n in range(nbatch):
        
        # try to replace with the batch string
        pattern = args.pattern
        output_file = args.output
        if args.batch is not None:
            print "processing batch string %s..." %args.batch[n]
            
            # do the pattern
            fmt_count = pattern.count('%s')
            if fmt_count > 0:
                fmt_strs = (args.batch[n])*fmt_count
                pattern = pattern %fmt_strs
                
            # and the output file
            fmt_count = output_file.count('%s')
            if fmt_count > 0:
                fmt_strs = (args.batch[n])*fmt_count
                output_file = output_file %fmt_strs
        
        # read the files
        results = glob(pattern)
        if not len(results):
            raise RuntimeError("whoops, no files match input pattern `%s`" %pattern)
        print "averaging %d files..." %len(results)
    
        # loop over each file
        data = []
        reader = files.Read2DPlainText if args.mode == '2d' else files.Read1DPlainText
        for f in results:
            try:
                d, m = reader(f)
            except Exception as e:
                raise RuntimeError("error reading `%s` as plain text file: %s" %(f, str(e)))
            
            if args.mode == '2d':
                d = dataset.Power2dDataSet.from_nbkit(d, m, sum_only=['modes'], force_index_match=True)
            else:
                d = dataset.Power1dDataSet.from_nbkit(d, m, sum_only=['modes'], force_index_match=True)
            data.append(d)
        
        
        # compute the average
        avg = average(data, sum_only=['modes'], weights='modes')
        io.write_plaintext(avg, output_file)
    
if __name__ == '__main__':
    main()
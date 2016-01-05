import argparse as ap
import os
import string
import tempfile

def my_string_parse(formatter, s, keys):
    l = list(string.Formatter.parse(formatter, s))
    toret = []
    for x in l:
        if x[1] in keys:
            toret.append(x)
        else:
            val = x[0]
            if x[1] is not None:
                fmt = "" if not x[2] else ":%s" %x[2]
                val += "{%s%s}" %(x[1], fmt)
            toret.append((val, None, None, None))
    return iter(toret)

def param_file(s):
    """
    A file holding parameters, which will be read, and returned
    as a string
    """
    if not os.path.exists(s):
        raise RuntimeError("file `%s` does not exist" %s)
    return open(s, 'r').read()

def extra_iter_values(s):
    """
    Provided an existing file name, read the file into 
    a dictionary. The keys are interpreted as the string format name, 
    and the values are a list of values to iterate over for each job
    """
    if not os.path.exists(s):
        raise RuntimeError("file `%s` does not exist" %s)
    toret = {}
    execfile(s, globals(), toret)
    return toret
  
def parse_args(desc, dims, coords):
    """
    Parse the command line arguments and return the namespace
    
    Parameters
    ----------
    desc : str
        the description for the argument parser
    dims : list of str
        the list of the dimensions for the samples
    coords : list of str
        the values corresponding to the sample dimensions
    
    Returns
    -------
    args : argparse.Namespace
        namespace holding the commandline arguments
    """
    
    parser = ap.ArgumentParser(description=desc)
                            
    h = 'the name of the job script to run. This file should take one' + \
        'command line argument ``param_file``, which specfies the template parameter file'
    parser.add_argument('job_file', type=str, help=h)
    h = 'the name of the file specifying the main power.py parameters'
    parser.add_argument('-p', '--config', required=True, type=param_file, help=h)
    h = 'the name of the file specifying the selection parameters'
    parser.add_argument('-s', '--select', default={}, type=extra_iter_values, help=h)
    h = 'the job submission mode'
    parser.add_argument('--mode', choices=['pbs', 'slurm'], default='pbs', help=h)
    
    # add the samples
    for i, (dim, vals) in enumerate(zip(dims, coords)):
        h = 'the #%d sample dimension' %i
        parser.add_argument('--%s' %dim, nargs='+', choices=['all']+vals, help=h, required=True)
    
    return parser.parse_args()

def submit_jobs(args, dims, coords, mode='pbs'):
    """
    Submit the job script specified on the command line for the desired 
    sample(s). This could submit several job at once, but will 
    wait 1 second in between doing so.  
    """
    import time
    import itertools
    
    if mode not in ['pbs', 'slurm']:
        raise ValueError("``mode`` must be `pbs` or `slurm`")
            
    # initialize a string formatter
    formatter = string.Formatter()
    
    # determine the samples we want to run
    samples = []
    for i, dim in enumerate(dims):
        val = getattr(args, dim)
        if len(val) == 1 and val[0] == 'all':
            val = coords[i]
        samples.append(val)
            
    # loop over each sample iteration
    for sample in itertools.product(*samples):
        
        # grab the kwargs to format for each dimension
        kwargs = {}
        for i, dim in enumerate(dims):
            name = '%s_%s' %(dim, sample[i])
            if name in args.select:
                kwargs.update(args.select[name])
        formatter.parse = lambda l: my_string_parse(formatter, l, kwargs.keys())
    
        # write out the formatted config file for this iteration
        all_kwargs = [kw for _, kw, _, _ in args.config._formatter_parser() if kw]
        with tempfile.NamedTemporaryFile(delete=False) as ff:
            fname = ff.name
            valid = {k:v for k,v in kwargs.iteritems() if k in all_kwargs}
            ff.write(formatter.format(args.config, **valid))
        
        param_str = 'param_file=%s' %fname
        if mode == 'pbs':
            x = "qsub -v '%s' %s" %(param_str, args.job_file)
        else:
            x = "sbatch \"--export=%s,ALL\" %s" %(param_str, args.job_file)
        print "calling %s..." %x
        ret = os.system(x)
        print "...done"
        time.sleep(1)

    
        
    
    
    
    
from nbodykit.extensionpoints import Transfer
import numpy

class MomentumMomentsEll(Transfer):
    """
    Transfer function for radial momentum moments
    """
    plugin_name = "MomentumMomentsEll"

    @classmethod
    def register(kls):
        h = kls.parser
        h.add_argument("moment", type=int, help="the radial velocity moment")

    def __call__(self, pm, complex):
        
        kern = 1.0 / numpy.math.factorial(self.moment)
        complex[:] *= kern
        
        
class MomentumMomentsEllPrime(Transfer):
    """
    Transfer function for radial momentum moments
    """
    plugin_name = "MomentumMomentsEllPrime"

    @classmethod
    def register(kls):
        h = kls.parser
        h.add_argument("moment", type=int, help="the radial velocity moment")

    def __call__(self, pm, complex):
        
        kern = (-1)**self.moment * 2.0 / numpy.math.factorial(self.moment)
        complex[:] *= kern
            


        
            

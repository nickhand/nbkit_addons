from nbodykit.extensionpoints import Transfer
import numpy


class MomentumMomentsAuto(Transfer):
    """
    Transfer function for radial momentum moments
    """
    plugin_name = "MomentumMomentsAuto"
    
    def __init__(self, ell):
        pass

    @classmethod
    def register(kls):
        h = kls.parser
        h.add_argument("ell", type=int, help="the radial velocity moment")
  
    def __call__(self, pm, complex):
        
        kern = 1.0 / numpy.math.factorial(self.ell)    
        complex[:] *= kern
        
class MomentumMomentsCross(Transfer):
    """
    Transfer function for radial momentum moments
    """
    plugin_name = "MomentumMomentsCross"
    
    def __init__(self, ell, ell_prime):
        pass

    @classmethod
    def register(kls):
        h = kls.parser
        h.add_argument("ell", type=int, help="the 1st radial velocity moment")
        h.add_argument("ell_prime", type=int, help="the 2nd radial velocity moment")
  
    def __call__(self, pm, complex):
        
        norm = numpy.math.factorial(self.ell) * numpy.math.factorial(self.ell_prime)
        if self.ell == self.ell_prime:
            kern = 1.0 / norm
        else:
            sign = (-1)**self.ell_prime * numpy.sign((1j)**(self.ell+self.ell_prime)).real
            kern = sign * (2. / norm)
            
        complex[:] *= kern
        
        
            


        
            

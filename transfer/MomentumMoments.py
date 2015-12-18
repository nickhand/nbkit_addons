from nbodykit.extensionpoints import Transfer
import numpy

class MomentumMoments(Transfer):
    """
    Transfer function for radial momentum moments
    """
    plugin_name = "MomentumMoments"

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
            power = self.ell + self.ell_prime + 1
            kern = (-1)**(power) * 2.0 / norm
        complex[:] *= kern
        
        
            


        
            

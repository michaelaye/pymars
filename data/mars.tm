KPL/MK

   This meta-kernel is a minimum meta kernel to enable geometrical calculations on the
   Martian surface without any S/C involvement

   \begindata
 
      PATH_VALUES     = (
                         '/Users/maye/data/spice/mars'
                         '/Users/maye/data/spice/gen'
                        )
 
      PATH_SYMBOLS    = (
						 'MY_KERNELS'
                         'GEN_KERNELS'
                        )
 
      KERNELS_TO_LOAD = (
                         '$MY_KERNELS/lsk/naif0010.tls'
                         '$GEN_KERNELS/pck/pck00008.tpc'
                         '$MY_KERNELS/spk/de421.bsp'
                        )
 
   \begintext
 


KPL/MK

   This meta-kernel is a minimum meta kernel to enable geometrical calculations on the
   Martian surface without any S/C involvement

 
   \begindata
 
      PATH_VALUES     = (
                         '/Users/maye/isis3/data/base/kernels'
						 '/Users/maye/data/spice/mars'
                        )
 
      PATH_SYMBOLS    = (
                         'BASE_KERNELS'
						 'MY_KERNELS'
                        )
 
      KERNELS_TO_LOAD = (
                         '$BASE_KERNELS/lsk/naif0009.tls'
                         '$BASE_KERNELS/pck/pck00008.tpc'
                         '$MY_KERNELS/spk/mar063.bsp'
                         '$MY_KERNELS/spk/de410.bsp'
                        )
 
   \begintext
 


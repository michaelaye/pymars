\begintext
   
   Several code examples mention use of a SPICE meta kernel 'standard.tm'. 
   Consider this as shorthand for any meta kernel that lists an SPK kernel, 
   PCK kernel, and a current leapseconds kernel.
   
   The names and contents of the kernels referenced by this meta-kernel 
   are as follows:

            File name                     Contents
            ---------                     --------
            de414.bsp                     Planetary ephemeris

            pck00008.tpc                  Planet orientation and
                                          radii

            naif0009.tls                  Leapseconds


   Load the three kernel: 


   \begindata

     KERNELS_TO_LOAD = ( '/Users/maye/isis3/data/base/kernels/lsk/naif0009.tls',
                         '/kernels/gen/spk/de414.bsp',
                         '/kernels/gen/pck/pck00008.tpc' )

   \begintext
   
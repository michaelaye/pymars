from collections import namedtuple

Planet = namedtuple('Planet',['mass',
                              'radius_equatorial',
                              'radius_polar',
                              'volume',
                              'flattening',
                              'surface_area',
                              'mean_density'])

Mars = Planet(mass = 6.4185e23,
             radius_equatorial = 3.3962e6,    # m
             radius_polar = 3.3762e6, # m
             volume = 1.6318e11,
             flattening = 0.00589,
             surface_area=144798500, # km**2
             mean_density=3.9335e3    # kg/m**3
             )
    
    
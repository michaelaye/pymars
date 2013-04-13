#!/usr/bin/env python
# encoding: utf-8


from __future__ import division
from traits.api import HasTraits, CFloat, CInt, List, Property
import numpy as np

class Euler(HasTraits):
    """class to practice Euler solution of thermal conduction"""
    # def __init__(self):
    #     super(Euler, self).__init__()
    tf = CFloat(0.05)
    N  = CInt(19)
    coeff_lambda = CFloat(0.4)
    dx = Property(depends_on='N')
    dt = Property(depends_on='coeff_lambda, dx')

    # x = List(np.arange(dx,N*dx+dx,dx))

    def _get_dx(self):
        """calculate dx when N changes"""
        return 1/(self.N+1)
    def _get_dt(self):
        """calculate dt when coeff_lambda and dx changes"""
        return self.coeff_lambda*self.dx**2
        
#     u0 = 1 - 2*abs(x-0.5)
#     t=0
#     un=u0
#     un1 = zeros(N)
#     while t<tf:
#         for j in arange(N):
#             un1[j]=(1-2*coeff_lambda)*un[j]
#             if j>1:
#                 un1[j] = un1[j] + coeff_lambda*un[j-1]
#             if j< N-1:
#                 un1[j]=un1[j]+coeff_lambda*un[j+1]
#         un = un1
#         plot(x,un)
#         t = t+dt
#     
# xx=append(append(0,x),1)
# u = append(append(0,un),0)
# ui=append(append(0,u0),0)
# 
# plot(xx,ui,'*',xx,u,'*')
# show()
euler = Euler()
euler.configure_traits()

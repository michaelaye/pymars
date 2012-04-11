#!/usr/bin/env python
# encoding: utf-8
"""
optics.py

Created by Klaus-Michael Aye on 2011-04-07.
Copyright (c) 2011 All rights reserved.
"""

import numpy as np

def fresnel_r_p(n1,n2,t_i):
    """Calculate parallel Fresnel reflection."""
    term1 = n1*sqrt(1-(n1*sin(deg2rad(theta_i))/n2)**2)
    term2 = n2*cos(deg2rad(theta_i))  
    n = (term1 - term2)*(term1 - term2)
    d = (term1 + term2)*(term1 + term2)
    return n/d

def fresnel_r_s(n1,n2,t_i):
    """Calculate s-polarised (perpendicular) Fresnel reflection."""
    term1 = n1*cos(deg2rad(theta_i))
    term2 = n2*sqrt(1-(n1*sin(deg2rad(theta_i))/n2)**2) 
    n = (term1 - term2)*(term1 - term2)
    d = (term1 + term2)*(term1 + term2)
    return n/d



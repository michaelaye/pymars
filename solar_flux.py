# thanks to the next line, you can do 2/3 and you get the correct thing!!
# this is the saviour for all scientists that don't program. ;)
from __future__ import division
from matplotlib.pylab import *


#---
# fixed parameters for now
#---
S_c = 1366 # solar constant
mu_0 = cos(deg2rad(45.0)) #
A = 0.7
tau = 0.1

# leave this for reference, even so it's only calculated once, always good
# to know where a number came from 
def calc_a():
    maxDist = 1.666 # [AU]
    minDist = 1.382 # [AU]
    return (maxDist + minDist) / 2

def get_R_h(L_s):
    """ provide L_s as heliocentric distance """
    delta = 0.000001
    e = 0.0934
    a = calc_a() #1.524 
    b = a * sqrt(1 - e ** 2)
    k = tan(deg2rad(L_s - 90.0))
    if L_s + delta > 0. and L_s + delta < 180.0:
        x = b * a * (e * b + sqrt(b ** 2 - (a * k * e) ** 2 + (a * k) ** 2)) / (b ** 2 + (a * k) ** 2)
    else:
        x = b * a * (e * b - sqrt(b ** 2 - (a * k * e) ** 2 + (a * k) ** 2)) / (b ** 2 + (a * k) ** 2)
    solution = abs(x) * sqrt(1 + k ** 2)
    return solution

def f_sol(R_h):
    term1 = S_c * (1 - A) * mu_0 / (R_h ** 2)
    term2 = exp(-tau / mu_0) + (tau / mu_0) * exp(-0.5 * tau / mu_0) * 0.35 * exp(-0.5 * tau)
    return term1 * term2

ls_arr = linspace(0, 360, 30)
rhs = map(get_R_h, ls_arr)

fig = figure(1)
# axes as plural is the matplotlib synomym for any plot, but you can call it
# what you want
axes = fig.add_subplot(211) 
for t in linspace(0.1, 1.0, 10):
    tau = t
    f_sols = map(f_sol, rhs)
    axes.plot(ls_arr, f_sols, label='tau=' + str(tau))
    axes.set_title('Solar Flux vs L_s, for different tau')
axes.axis('tight')
axes.legend()    
tau = 0.1
axes2 = fig.add_subplot(212)
for alb in linspace(0.3, 0.8, 6):
    A = alb
    f_sols = map(f_sol, rhs)
    axes2.plot(ls_arr, f_sols, label='A=' + str(A))
    axes2.set_title('Solar Flux vs L_s, for different albedos')
axes2.legend()    
# plotting is done in memory, until you give the show() command
# this way is much faster, than to plot all the time
show()

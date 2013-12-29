from visual import *
from time import clock
from visual.graph import *
from random import random

# A model of an ideal gas with hard-sphere collisions
# Program uses Numeric Python arrays for high speed computations
# Modified from the uncredited demo code (gas.py) from the VPython distribution
#  by Lensyl Urbano - January, 2005 - to change color and ke when the
#  temperature is changed with a slider.

# adapted by K.-Michael Aye, 2013
# made classes inherit from object

l_slomo = 0
slomo = 4.0

class hslider(object):
    "horizontal slider that is not in the control window"
    def __init__(self, pos, L, mini, maxi, init=None):
        self.bar = cylinder(pos=pos, axis = (L,0.0,0.0), color = (1,0,0), radius = L/80.0)
        self.but = sphere(pos=pos, color = (0,0,1), radius = L/40)
        self.min = mini
        self.max = maxi
        self.init = mini
        if init:
            self.but.pos.x = self.but.pos.x + ((init-mini) / (maxi-mini))*L

class T_change_event(object):
    "horizontal slider that is not in the control window"
    def __init__(self, tstart, tend, finT):
        self.start = tstart     #event starttime
        self.end = tend         #event end time
        self.finT = finT    #angle of rotation in degrees
        self.type = "T change"
        self.init = 1

def atom_color(ke):
    #ke_max = 1e-23 * (1.0-((T_max - T)/T_max))
    rmax = 2.5e-24
    gmax = 7.5e-24
    bmax = 1e-23
    if ke < rmax:
        r = ke / rmax
        b = 0.0
        g = 0.0
    elif ke < gmax:
        r = max(0.0, (gmax-ke)/gmax)
        g = 1.0 - r
        b = 0.0
    else:
        r = 0.0
        g = max(0.0, (bmax-ke)/bmax)
        b = 1.0 - g
    #print ke, ke/rmax, r, b
    col = vector(r, g, b)
    return col

win=500

Natoms = 50  # change this to have more or fewer atoms

# Typical values
L = 1. # container is a cube L on a side
gray = (0.7,0.7,0.7) # color of edges of container
Raxes = 0.005 # radius of lines drawn on edges of cube
Matom = 4E-3/6E23 # helium mass
Ratom = 0.03 # wildly exaggerated size of helium atom
k = 1.4E-23 # Boltzmann constant
T = 300. # around room temperature
dt = 1E-5

Ladj = L

##scene = display(title="Gas", width=win, height=win, x=0, y=0,
##                range=L, center=(L/2.,L/2.,L/2.))
scene = display(title="Gas", range=L*1.1, center=(L/2.,L/2.,L/2.))
origx = 0
origy = 0
w = 704+4+4
h = 576 #+24+4
low_win = 80
scene.width=w
scene.height=h #- low_win
scene.x = origx
scene.y = origy
#scene.ambient = 0.5
#scene.lights[0] =  2* vector(0.17, 0.35, 0.70)
#scene.background = vector(1,1,1)

xaxis = curve(pos=[(0,0,0), (L,0,0)], color=gray, radius=Raxes)
yaxis = curve(pos=[(0,0,0), (0,L,0)], color=gray, radius=Raxes)
zaxis = curve(pos=[(0,0,0), (0,0,L)], color=gray, radius=Raxes)
xaxis2 = curve(pos=[(L,L,L), (0,L,L), (0,0,L), (L,0,L)], color=gray, radius=Raxes)
yaxis2 = curve(pos=[(L,L,L), (L,0,L), (L,0,0), (L,L,0)], color=gray, radius=Raxes)
zaxis2 = curve(pos=[(L,L,L), (L,L,0), (0,L,0), (0,L,L)], color=gray, radius=Raxes)

scene.background = color.white

Atoms = []
colors = [color.red, color.green, color.blue,
          color.yellow, color.cyan, color.magenta]
poslist = []
plist = []
mlist = []
rlist = []

for i in range(Natoms):
    Lmin = 1.1*Ratom
    Lmax = L-Lmin
    x = Lmin+(Lmax-Lmin)*random()
    y = Lmin+(Lmax-Lmin)*random()
    z = Lmin+(Lmax-Lmin)*random()
    r = Ratom
    Atoms = Atoms+[sphere(pos=(x,y,z), radius=r, color=colors[i % 6])]
    mass = Matom*r**3/Ratom**3
    pavg = sqrt(2.*mass*1.5*k*T) # average kinetic energy p**2/(2mass) = (3/2)kT
    theta = pi*random()
    phi = 2*pi*random()
    px = pavg*sin(theta)*cos(phi)
    py = pavg*sin(theta)*sin(phi)
    pz = pavg*cos(theta)
    poslist.append((x,y,z))
    plist.append((px,py,pz))
    mlist.append(mass)
    rlist.append(r)

pos = array(poslist)
p = array(plist)
m = array(mlist)
m.shape = (Natoms,1) # Numeric Python: (1 by Natoms) vs. (Natoms by 1)
radius = array(rlist)

t = 0.0
Nsteps = 0
pos = pos+(p/m)*(dt/2.) # initial half-step
time = clock()

#ldu
ptot = pavg * Natoms
T_mod = 1.0
T_mod_old = T_mod

#create control window
cwin = display(title="Temperature Control", width=w, height=low_win,
               x=0, y=h-low_win,
               center = (L/2.0,0,0), range = L)

#create sliders
Tbar = cylinder(pos=(0,0,0), color = (1,0,0), axis=(L,0,0), radius = L/80.0)
Tball = sphere(pos=(L, 0, 0), color = (0,0,1), radius = L/40)
T_init = T
dt_init = dt

##Vbar = cylinder(pos=(0,L/6.0,0), color = (1,0,0), axis=(L,0,0), radius = L/80.0)
##Vball = sphere(pos=(L, L/6.0,0), color = (0,0,1), radius = L/40)


events = []
##events.append(T_change_event(5.0, 10.0, T / 2.0))
##events.append(T_change_event(15.0, 20.0, 300.0))
##
framerate = T_init
runtime = 0
pick = None

while 1:
    rate(60)
    runtime += 1.0/framerate
    if l_slomo == 1:
        rate(slomo)

    #change temperature
    
        
    if cwin.mouse.events:
        m1 = cwin.mouse.getevent() # obtain drag or drop event
        if m1.drag and (m1.pick == Tball or m1.pick == vol.but):
            drag_pos = m1.pickpos
            pick = m1.pick
            cwin.cursor.visible = 0 # make cursor invisible
        elif m1.drop:
            pick = None # end dragging
            cwin.cursor.visible = 1 # cursor visible
            
    if pick:
        new_pos = cwin.mouse.project(normal=(0,0,1),point=(0,0,0))
        if new_pos != drag_pos and (new_pos.x > 0 and new_pos.x < L):
            pick.pos.x += new_pos.x - drag_pos.x
            drag_pos = new_pos
        elif (new_pos.x < 0.0): 
            pick.pos.x = 0.0
        elif (new_pos.x > L): 
            pick.pos.x = L


    #update box size
    xaxis.pos[1]=(Ladj,0,0)
    yaxis.pos[1]=(0,Ladj,0)
    zaxis.pos[1]=(0,0,Ladj)
    xaxis2.pos=[(Ladj,Ladj,Ladj), (0,Ladj,Ladj), (0,0,Ladj), (Ladj,0,Ladj)]
    yaxis2.pos=[(Ladj,Ladj,Ladj), (Ladj,0,Ladj), (Ladj,0,0), (L,Ladj,0)]
    zaxis2.pos=[(Ladj,Ladj,Ladj), (Ladj,Ladj,0), (0,Ladj,0), (0,Ladj,Ladj)]

    #update temperature and ke
    T_mod = Tball.pos.x / L     #New temperature
    T_mod = max(T_mod, 0.01)
    T_modf = T_mod / T_mod_old
    #print T_mod, pavg
    if T_mod <> T_mod_old:
        p = p * T_modf
    T_mod_old = T_mod

    # Update all positions
    pos = pos+(p/m)*dt

    try:
        r = pos-pos[:,newaxis] # all pairs of atom-to-atom vectors
        #print r
    except:
        r = pos-pos[:,newaxis] # all pairs of atom-to-atom vectors
    rmag = sqrt(add.reduce(r*r,-1)) # atom-to-atom scalar distances
    try:
        hit = less_equal(rmag,radius+radius[:,newaxis])-identity(Natoms)
    except:
        hit = less_equal(rmag,radius+radius[:,NewAxis])-identity(Natoms)
    hitlist = sort(nonzero(hit.flat)).tolist() # i,j encoded as i*Natoms+j
    #print hit

    # If any collisions took place:
    #print "hitlist", hitlist, hitlist[0]
    for ij in hitlist[0]:
        #print ij, Natoms
        i, j = divmod(ij,Natoms) # decode atom pair
        hitlist[0].remove(j*Natoms+i) # remove symmetric j,i pair from list
        ptot = p[i]+p[j]
        mi = m[i,0]
        mj = m[j,0]
        vi = p[i]/mi
        vj = p[j]/mj
        ri = Atoms[i].radius
        rj = Atoms[j].radius
        a = mag(vj-vi)**2
        if a == 0: continue # exactly same velocities
        b = 2*dot(pos[i]-pos[j],vj-vi)
        c = mag(pos[i]-pos[j])**2-(ri+rj)**2
        d = b**2-4.*a*c
        if d < 0: continue # something wrong; ignore this rare case
        deltat = (-b+sqrt(d))/(2.*a) # t-deltat is when they made contact
        pos[i] = pos[i]-(p[i]/mi)*deltat # back up to contact configuration
        pos[j] = pos[j]-(p[j]/mj)*deltat
        mtot = mi+mj
        pcmi = p[i]-ptot*mi/mtot # transform momenta to cm frame
        pcmj = p[j]-ptot*mj/mtot
        rrel = norm(pos[j]-pos[i])
        pcmi = pcmi-2*dot(pcmi,rrel)*rrel # bounce in cm frame
        pcmj = pcmj-2*dot(pcmj,rrel)*rrel
        p[i] = pcmi+ptot*mi/mtot # transform momenta back to lab frame
        p[j] = pcmj+ptot*mj/mtot
        pos[i] = pos[i]+(p[i]/mi)*deltat # move forward deltat in time
        pos[j] = pos[j]+(p[j]/mj)*deltat
        #ldu
##        pfac[i] = p[i]/pavg
##        pfac[j] = p[j]/pavg
        #print mag(p[i])
##        Atoms[i].color = atom_color(mag(p[i]), dt, dt_init)
##        Atoms[j].color = atom_color(mag(p[j]), dt, dt_init)


    # Bounce off walls
    outside = less_equal(pos,Ratom) # walls closest to origin
    p1 = p*outside
    p = p-p1+abs(p1) # force p component inward
    outside = greater_equal(pos,L-Ratom) # walls farther from origin
    p1 = p*outside
    p = p-p1-abs(p1) # force p component inward

    #print max(p), min(p)
    # Update positions of display objects
    for i in range(Natoms):
        Atoms[i].pos = pos[i]
        #print p[i]
        Atoms[i].color = atom_color(mag(p[i]))

    Nsteps = Nsteps+1
    t = t+dt

    for e in events:
        if runtime >= e.start and runtime <= e.end:
            if e.type == "T change":
                if e.init == 1:
                    e.init = 0
                    Tchange = (T_mod - e.finT) / (framerate * L)
                    Tsch = (Tball.pos.x - (e.finT/T)) / (framerate * (e.end - e.start))
                    #print "Tball.pos.x, e.finT, Txch = ", Tball.pos.x, e.finT, Tsch
                Tball.pos.x = Tball.pos.x - Tsch
                #T_mod = T_mod + Tchange
                #print "Tchange, T_mod", Tchange, Tball.pos.x



##    if Nsteps == 50:
##        print '%3.1f seconds for %d steps with %d Atoms' % (clock()-time, Nsteps, Natoms)
##    rate(30)

#########################################
# Import the libraries
#########################################
from visual import *
from visual.controls import *
from time import clock
from visual.graph import *
from random import random

# A model of an ideal gas with hard-sphere collisions
# Giulio Venezian  <gvenezian@yahoo.com> 2010

## Program uses numpy arrays for high speed computations.
## Based on gas.py, which is distributed in the VPython example programs.
##   modified so initial distribution has no overlapping atoms
##   modified for isotropic distribution (but all atoms start with the same energy)
##   modified to display additional histograms
## This is an attempt to handle collisions in the order they occur;
## in previous versions, they were handled by position in the loop, not in order of occurrence
## which makes the system irreversible (aside from rounoff errors).

def reset():
    setdefaultsituation()
    pause(state=1)
    breset.state = 1
##    restoreview()
def click():
    # return 1 if click in main window
    if scene.mouse.events:
        m = scene.mouse.getevent()
        return m.click
    else:
        return 0
def pause(state=None):
    if state != None:
        bpause.state = state
    else:
        bpause.state = not bpause.state
    if bpause.state:
        bpause.text = 'Run'
    else:
        bpause.text = 'Pause'
def update2():   
    Pxvalue=press
    labQ.text="%.6e"%Pxvalue
###########################################
# Problem parameters
###########################################
win=300 ##pixels for graph widths and position

Natoms = 10 # change this to have more or fewer atoms

# Typical values
L = 1. # container is a cube L on a side
gray = (0.7,0.7,0.7) # color of edges of container
Raxes = 0.005 # radius of lines drawn on edges of cube
Matom = 4E-3/6E23 # helium mass
Ratom = 0.05 # wildly exaggerated size of helium atom
Ratom=.1
k = 1.4E-23 # Boltzmann constant
T = 300. # around room temperature
##calculated parameters:
V=(L-Ratom)**3 ##available volume
pressure=Natoms*k*T/V
print 'Number of Atoms',Natoms
print 'Temperature', T
print 'Volume', V
print 'Pressure', pressure



###########################################
# Set up Histogram Plot for speeds
###########################################
deltav = 100. # binning for v histogram
vdist = gdisplay(x=0, y=win, ymax = Natoms*deltav/1000.,
             width=win, height=win/2., xtitle='v', ytitle='dN',
                 title="Distribution of v")
theory = gcurve(color=color.green)
observation = ghistogram(bins=arange(0.,3000.,deltav),
                        accumulate=1, average=1, color=color.red)

dv = 10.
for v in arange(0.,3001.+dv,dv): # theoretical prediction
    theory.plot(pos=(v,
        (deltav/dv)*Natoms*4.*pi*((Matom/(2.*pi*k*T))**1.5)
                     *exp((-0.5*Matom*v**2)/(k*T))*v**2*dv))

###########################################
# Set up Histogram Plot for x-velocity
###########################################
# add the same for vx
deltavx = 200. # binning for vx histogram
vxdist = gdisplay(x=0, y=int(1.5*win), ymax = Natoms*deltavx/1000.,
             width=win, height=win/2., xtitle='vx', ytitle='dN',
                 title="Distribution of vx")
theoryvx = gcurve(color=color.green)
observationvx = ghistogram(bins=arange(-3000.,3000.,deltavx),
                        accumulate=1, average=1, color=color.orange)

dvx = 10.
for vx in arange(-(3000.+dvx),3000.+dvx,dvx): # theoretical prediction
    theoryvx.plot(pos=(vx,Natoms*deltavx*(Matom/(2.*pi*k*T))**0.5
                     *exp((-0.5*Matom*vx**2)/(k*T))))



###########################################
# Set up Histogram Plot for density in x
###########################################
# add the same for x
deltax = 0.1*(L-2*Ratom) # binning for x histogram
xdist = gdisplay(x=win,y=win, ymax = Natoms/5.,
             width=win, height=win/2., xtitle='x', ytitle='dN',
                 title="Distribution of x")
theoryx = gcurve(color=color.green)
observationx = ghistogram(bins=arange(Ratom,L-2*Ratom,deltax),
                        accumulate=1, average=1, color=color.orange)

dx = .05
for x in arange(0,1+dx,dx): # theoretical prediction
    theoryx.plot(pos=(x,Natoms*deltax))
###########################################
# Set up Histogram Plot for Energy
###########################################
deltaE = 1.e-21 # binning for E histogram
Edist = gdisplay(xmin=0.,xmax=2.e-20, x=win,y=int(.5*win), ymax = Natoms/2.,
             width=win, height=.5*win, xtitle='E', ytitle='dN',
                 title="Distribution of Energy")
theoryE = gcurve(color=color.green)
observationE = ghistogram(bins=arange(0,2.e-20,deltaE),
                        accumulate=1, average=1, color=color.orange)

dE = 1.e-21
for E in arange(0,2.e-20+dE,dE): # theoretical prediction
    theoryE.plot(pos=(E,Natoms*2.*(E/pi/k/T)**(.5)*exp(-E/(k*T))*deltaE/(k*T)))
###########################################
## Set up Histogram of Free Paths (atom-to-atom)
###########################################
deltal=2.
fpdist = gdisplay(xmin=-0.1,xmax=40., x=win,y=int(1.5*win), ymax = Natoms/4.,
             width=win, height=win/2., xtitle='x', ytitle='dN',
                 title="Distribution of free paths")
sigma=4.*pi*Ratom**2 ##collision cross-section
Vol=(L-Ratom)**3
meanfp=Vol/sigma/(Natoms-1)##mean free path
print 'meanfp',meanfp
theoryl = gcurve(color=color.green)
observationfp = ghistogram(bins=arange(0,40.,deltal),
                        accumulate=1, average=1, color=color.orange)

dfp = 1.
for fp in arange(0,40.+dfp,dfp): # theoretical prediction
    theoryl.plot(pos=(fp,Natoms*exp(-fp/meanfp)*deltal/meanfp))
###########################################
##add windows for future additions
###########################################
##pgraph = gdisplay(xmin=-0.1,xmax=1., x=win,y=.5*win, ymax = Natoms/5.,
##             width=win, height=win/2., xtitle='x', ytitle='dN',
##                 title="Pressure")
##panel = gdisplay(xmin=-0.1,xmax=1., x=2.*win,y=0, ymax = Natoms/5.,
##             width=.7*win, height=2*win, xtitle='x', ytitle='dN',
##                 title="Control panel")
ctrl = controls(x=2*win, y=0, width=.7*win, height=2*win, title='Control Panel')
bpause = button(pos=(0,30), width=60, height=30,
             action=lambda: pause())
##brepeat = button(pos=(0,60), width=60, height=30, text='Repeat',
##             action=lambda: repeat())
##benergy = button(pos=(0,90), width=60, height=30,
##             action=lambda: energy())
##bget = button(pos=(0,0), width=60, height=30, text='Get File',
##              action=lambda: getsituation())
##bsave = button(pos=(0,-30), width=60, height=30, text='Save File',
##              action=lambda: savesituation())
##breset = button(pos=(0,-60), width=60, height=30, text='Reset',
##             action=lambda: reset())
##pause(state=1)
##bget.state = 0
##breset.state = 0
##brepeat.state = 0
##########################################
# Prepare graph of pressure
##########################################
pR_graph = gdisplay(x=win,y=0, ymax = 1.e-19,
             width=win, height=win/2., xtitle='t', ytitle='press',
                 title="Average Pressure on right wall")
avpR_Plot=gcurve(color=color.green)
##########################################
# Prepare a digital readout screen
##########################################
impulseR=0 #cumulative impulse on right wall
scene2 = display(title='Pressure',
     x=win,y=2*win,width=150, height=150,
     center=(0,0,0), background=(0.25,0.25,0.25))
##
##
Pxvalue=0
labQ=label(pos=(0,0,0), text="%.6e" % Pxvalue,opacity=0.,
           box=0,color=color.green)

scene2.visible=1
scene2.userspin=0
scene2.userzoom=0
scene2.autoscale=0
##


###########################################
# Set up Display of Atoms
###########################################
scene = display(title="Ideal Gas", width=win, height=win, x=0, y=0,
                range=L, center=(L/2.,L/2.,L/2.))
##########################################
# Create the Box
##########################################
xaxis = curve(pos=[(0,0,0), (L,0,0)], color=gray, radius=Raxes)
yaxis = curve(pos=[(0,0,0), (0,L,0)], color=gray, radius=Raxes)
zaxis = curve(pos=[(0,0,0), (0,0,L)], color=gray, radius=Raxes)
xaxis2 = curve(pos=[(L,L,L), (0,L,L), (0,0,L), (L,0,L)], color=gray, radius=Raxes)
yaxis2 = curve(pos=[(L,L,L), (L,0,L), (L,0,0), (L,L,0)], color=gray, radius=Raxes)
zaxis2 = curve(pos=[(L,L,L), (L,L,0), (0,L,0), (0,L,L)], color=gray, radius=Raxes)

Atoms = []
colors = [color.red, color.green, color.blue,
          color.yellow, color.cyan, color.magenta]
poslist = []
plist = []
mlist = []
rlist = []
pxlist=[]
xlist=[]
##########################################
# populate box with atoms
##########################################
## section modified to prevent molecules from overlapping each other
## for this test, put all the molecules in the left half
n=0
while n<Natoms:
    Lmin = 1.001*Ratom
    Lmax = L-Lmin
    x = Lmin+(Lmax-Lmin)*random()
    y = Lmin+(Lmax-Lmin)*random()
    z = Lmin+(Lmax-Lmin)*random()
    r = Ratom
    mass = Matom*r**3/Ratom**3
    pavg = sqrt(2.*mass*1.5*k*T) # average kinetic energy p**2/(2mass) = (3/2)kT

    if n==0:
        n+=1
        poslist.append((x,y,z))
        rlist.append(r)
        xlist.append(x)
        pos = array(poslist)
        radius = array(rlist)
        phi=random()*(2.*pi)
        costheta=1.-2.*random()
        sintheta=(1-costheta**2)**.5
        px = pavg*sintheta*cos(phi)
        py = pavg*sintheta*sin(phi)
        pz = pavg*costheta
        plist.append((px,py,pz))
        mlist.append(mass)
        pxlist.append(px)
        Atoms = Atoms+[sphere(pos=(x,y,z), radius=r, color=colors[n % 6])]
#### To test for reversibility make the spheres in different portions of the box different colors
##        if x<.5:
##            col=color.red
##        else:
##            col=color.white
##        Atoms = Atoms+[sphere(pos=(x,y,z), radius=r, color=col)]
    else:
        dr=pos-array([x,y,z])
        drmag = sqrt(add.reduce(dr*dr,-1))
        ##test for overlap; reject if atom overlaps atoms that are there
        if (drmag>radius+r).all():
            n+=1
            poslist.append((x,y,z))
            rlist.append(r)
            xlist.append(x)
            pos = array(poslist)
            radius = array(rlist)
            mass = Matom*r**3/Ratom**3
        
            Atoms = Atoms+[sphere(pos=(x,y,z), radius=r, color=colors[n % 6])]
#### To test for reversibility make the spheres in different portions of the box different colors
##            if x<.5:
##                col=color.red
##            else:
##                col=color.white
##            Atoms = Atoms+[sphere(pos=(x,y,z), radius=r, color=col)]
##########################################
# Initialize momenta
##########################################
### These are the corrected forms for an
### isotropic distribution but with all the atoms at one energy
            phi=random()*(2.*pi)
            costheta=1.-2.*random()
            sintheta=(1-costheta**2)**.5
            px = pavg*sintheta*cos(phi)
            py = pavg*sintheta*sin(phi)
            pz = pavg*costheta
            plist.append((px,py,pz))
            mlist.append(mass)
            pxlist.append(px)
p = array(plist)
m = array(mlist)
m.shape = (Natoms,1) # specify column vector. Numeric Python: (1 by Natoms) vs. (Natoms by 1)
mrow=array(mlist)
pxarray=array(pxlist)
Earray=add.reduce(p*p,-1)/mrow/2.
xarray=array(xlist)
larray=zeros(Natoms) #distance traveled since last atom-to-atom even
collarray=zeros(Natoms) #array of free paths

###########################################
# Advance molecules to new positions
###########################################
nsteps=0
##ntest=100
pause(state=0)
st=0 ##pause state
tcoll=0.## time
impulseR=0 #cumulative impulse on right wall
while 1:
    rate(60)
    ctrl.interact()
##    if click() or breset.state or brepeat.state or bget.state:
    if click():
        pause(state=1-st)
        st=1-st
    if not bpause.state:
##    ##  To test for reversibility add these:
##        if nsteps==ntest: p=-p
##        if nsteps==2*ntest:pause(state=1)
        
        v=p/m
        observation.plot(data=mag(p/m))
        observationvx.plot(data=(pxarray/mrow))
        observationx.plot(data=xarray)
        observationE.plot(data=Earray)
        #####################
        ## wall collisions
        ## find time interval to the next impending collision with a wall
        ## assuming that there are no intermolecular collisions
        
        ## prevent division by zero
        dtwall=1e99
        for k in range(Natoms):
            lw=-1
            for l in range(3):
                dt=2.e99
                if v[k,l]>0.:
                    dt=(Lmax-pos[k,l])/v[k,l]
                    lw=l
                if v[k,l]<0.:
                    dt=(Lmin-pos[k,l])/v[k,l]
                    lw=l+3
                if dt<dtwall:
                    dtwall=dt
                    lwall=l
                    nwall=lw ##keeps track of which wall was hit for pressure calculation
                    kwall=k  ##keeps track of which molecule hit the wall
        ######################
        ## atom-to-atom collisions
        ## find time of next impending atom-to-atom collision
        ## without regard to the walls
                    
        dtamom=1.e99
        ##construct arrays of relative positions and relative velocities
        rrellist=[]
        vrellist=[]
        dminlist=[]
        for i in range(Natoms-1):
            for j in range(i+1,Natoms):
                dr=pos[j]-pos[i]
                dv=v[j]-v[i]
                rrellist.append(dr)
                vrellist.append(dv)
                dminlist.append(radius[j]+radius[i])##closest allowable distance
        rrel=array(rrellist)
        vrel=array(vrellist)
        dmin=array(dminlist)##this calculation doesn't have to be repeated
        rmag = sqrt(add.reduce(rrel*rrel,-1))##array of magnitudes of relative positions 
        vmag = sqrt(add.reduce(vrel*vrel,-1))##array of magnitudes of relative velocities
        dotrv = add.reduce(rrel*vrel,-1)##array of dot products
        ##this seems to be the best way to get the array of dot products
        prodmag = rmag*vmag
        crv = dotrv/prodmag##array of cosines
        ###################################
        ##  calculate array of distances of closest approach
        d = rmag*sqrt(1-crv**2)
        ##time for collision
        ##for positive time, dot product must be negative
        ##for collision to occur, dmin >d
        dtatom=1.e9
        imin=-1
        for i in range(Natoms*(Natoms-1)/2):
            if dotrv[i]<0:
                if dmin[i]>d[i]:
                    dt=(sqrt(rmag[i]**2-d[i]**2)-sqrt(dmin[i]**2-d[i]**2))/vmag[i]
                    if dt>0:
                        if dt<dtatom:
                            dtatom=dt
                            imin=i
    ##update positions and velocities

        if dtatom<dtwall:
            tcoll+=dtatom
            pos+=v*dtatom
            ##figure out which two atoms are colliding
            N=Natoms
            im=imin
            iz=0
            while N>0:
                if im<N-1:
                    i=iz
                    j=im+i+1
                    N=0
                else:
                    N=N-1
                    im=im-N
                    iz=iz+1
            ##update distance traveled by molecules
            vmag = sqrt(add.reduce(v*v,-1))##array of speeds
##            print larray,vmag*dtatom
            larray+=vmag*dtatom##once in a while this line gives an error. Why?
            observationfp.plot(data=collarray)
            collarray[i]= 0.+larray[i]
            collarray[j]=0.+larray[j]
##            print imin,i,j,larray[i],larray[j],collarray[i],collarray[j]
            larray[i]=0
            larray[j]=0
            ## fix the momenta
            deltap=2*m[i]*m[j]*dotrv[imin]*rrel[imin]/(m[i]+m[j])/rmag[imin]**2
            p[i]=p[i]+deltap
            p[j]=p[j]-deltap
            v=p/m

        if dtwall<=dtatom:
            pos+=v*dtwall
            tcoll+=dtwall
            ##update distance traveled by molecules
            vmag = sqrt(add.reduce(v*v,-1))##array of speeds
##            print larray,vmag*dtwall
            larray=larray+vmag*dtwall
            if nwall==0:
                impulseR+=2.*m[kwall]*v[kwall,nwall]
                press=impulseR[0]/tcoll/L**2
                ##print 'press',press
                #######################################
                # Plot the wall pressure
                #######################################
                avpR_Plot.plot(pos=(tcoll,press))
                update2()


            ##  reverse the normal velocity
            v[kwall,lwall]=-v[kwall,lwall]
            p=v*m
        nsteps+=1
        Earray=add.reduce(p*p,-1)/mrow/2.


        #####################################
        # Update display objects
        #####################################
        for i in range(Natoms):
            Atoms[i].pos = pos[i]
            # need to update x and vx as well
            xarray[i]=pos[i,0]
            pxarray[i]=p[i,0]
    


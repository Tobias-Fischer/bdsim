#!/usr/bin/env python3

# run with command line -a switch to show animation

import bdsim

sim = bdsim.BDSim()
bd = sim.blockdiagram()
    
steer = bd.PIECEWISE( (0,0), (3,0.5), (4,0), (5,-0.5), (6,0), name='steering')
speed = bd.CONSTANT(1, name='speed')
bike = bd.BICYCLE(x0=[0, 0, 0], name='bicycle')

tscope= bd.SCOPE(name='theta')
scope = bd.SCOPEXY(scale=[0, 10, 0, 1.2])

bd.connect(speed, bike[0])
bd.connect(steer, bike[1])

bd.connect(bike[0:2], scope)
bd.connect(bike[2], tscope)

bd.compile()
bd.report()

out = sim.run(bd, dt=0.05)

sim.savefigs(bd, format='pdf')

bd.done(block=True)

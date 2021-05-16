from bdsim import BDSim

PWM_FREQ = 20

sim = BDSim(backend='TkAgg')
bd = sim.blockdiagram()

clock = bd.clock(50, 'Hz')

duty = bd.TIME()  # essentially a ramp input

approx = bd.PWM(clock, duty, freq=PWM_FREQ, v_range=(0, 3.3))
actual = bd.PWM(clock, duty, freq=PWM_FREQ, v_range=(0, 3.3), approximate=False)

scope = bd.SCOPE(labels=["Duty Cycle", "Approx PWM V", "Actual PWM V"],
                 stairs=[False, True, True])
scope[0] = duty
scope[1] = approx
scope[2] = actual

bd.compile()

sim.run(bd, T=1, dt=1 / PWM_FREQ / 10)
sim.done(bd, block=True)

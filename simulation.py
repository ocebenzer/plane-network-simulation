import simpy

from utils import *
from network import Plane, GroundStation

plane_counter = 0
def plane_generator(env: simpy.Environment, mplane: float, mpacket: float, distance: float):
    ground_start = GroundStation("start", 0)
    ground_end = GroundStation("end", distance)
    last_node = ground_start
    while True:
        yield env.timeout(mplane)
        plane = Plane(mpacket) 
        env.process(plane.take_off(env, ground_start, ground_end, last_node))
        last_node = plane

# t: simulation time
# mplane: plane take off interarrival
# mpacket: plane take off interarrival
# distance: plane route distance
def simulation(t=12*H, mplane=30*MIN, mpacket=50*MS, distance=5000*KM):# todo set mpacket 50MCS
    env = simpy.Environment()
    env.process(plane_generator(env, mplane, mpacket, distance))

    env.run(until=t)

simulation()

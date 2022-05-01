import simpy

from network import GroundStation, Plane
from utils import *

ground_start = GroundStation()
ground_end = GroundStation()
plane_counter = 0
def plane_generator(env: simpy.Environment, mp: float):
    last_node = ground_start
    while True:
        yield env.timeout(mp)
        plane = Plane()
        env.process(plane.take_off(env, 5000*KM, last_node, ground_start))
        last_node = plane

# t: simulation time
# mp: plane take off interarrival
def simulation(t=12*H, mp=30*MIN):
    env = simpy.Environment()

    env.process(plane_generator(env, mp))

    env.run(until=t)

simulation()

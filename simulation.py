import simpy

from utils import *
from network import Plane, Packet, GroundStation

planes = []
def plane_generator(env: simpy.Environment, mplane: float, mpacket: float, mprocess: float, buffer_size: int, distance: float):
    ground_start = GroundStation("start", 0)
    ground_end = GroundStation("end", distance)
    last_node = ground_start
    while True:
        plane = Plane(mpacket, mprocess, buffer_size)
        env.process(plane.take_off(env, ground_start, ground_end, last_node))
        last_node = plane
        planes.append(plane)
        yield env.timeout(mplane)

def clock(env: simpy.Environment):
    while True:
        yield env.timeout(1*MIN)
        log(env)

# t: simulation time
# mplane: plane take off interarrival
# mpacket: packet creation (per plane) interarrival
# mprocess: packet process (per plane) delay
# buffer_size: packet buffer size (per plane)
# distance: plane route distance
def simulation(t=24*H, mplane=30*MIN, mpacket=50*MS, mprocess=2*MS, buffer_size=20, distance=6000*KM):
    env = simpy.Environment()
    
    env.process(plane_generator(env, mplane, mpacket, mprocess, buffer_size, distance))
    #env.process(clock(env))

    env.run(until=t)
    print("-- Simulation Complete --")
    print(f"Success Ratio\t{Packet.created - Packet.dropped}/{Packet.created} ({(Packet.created - Packet.dropped)/Packet.created*100:.2f}%)")
    print(f"Avg. latency\t{Packet.total_delay / Packet.transfered /MS:5.4f}ms")
    print(f"Dropped\t\t{Packet.dropped}")
    pass

simulation()

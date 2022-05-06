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
        log(env, end="\r")

# t: simulation time
# mplane: plane take off interarrival
# mpacket: packet creation (per plane) interarrival
# mprocess: packet process (per plane) delay
# buffer_size: packet buffer size (per plane)
# distance: plane route distance
# ptransmission: success chance of a packet at 200km distance
def simulation(t=1*H, mplane=15*MIN, mpacket=50*MS, mprocess=2*MS, buffer_size=10, distance=6000*KM, ptransmissionAT200=0.999):
    env = simpy.Environment()
    Plane.set_gamma(ptransmissionAT200)

    env.process(plane_generator(env, mplane, mpacket, mprocess, buffer_size, distance))
    env.process(clock(env))

    env.run(until=t)
    print("-- Simulation Complete --")
    print(f"Success Ratio\t{Packet.created - Packet.dropped_buffer - Packet.dropped_transmission}/{Packet.created} ({(Packet.created - Packet.dropped_buffer - Packet.dropped_transmission)/Packet.created*100:.2f}%)")
    print(f"Avg. latency\t{Packet.total_delay / Packet.transfered /MS:5.4f}ms")
    print(f"Dropped due to buffer\t\t{Packet.dropped_buffer}")
    print(f"Dropped due to transmission\t{Packet.dropped_transmission}")
    pass

simulation()

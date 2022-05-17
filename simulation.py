import simpy

from utils import *
from network import Plane, Packet, GroundStation

planes = []
def plane_generator(env: simpy.Environment, mplane: float, mpacket: float, mprocess: float, buffer_size: int, plane_speed: float, distance: float, simulation_starttime: float):
    ground_start = GroundStation("start", 0)
    ground_end = GroundStation("end", distance)
    last_node = ground_start
    while True:
        plane = Plane(mpacket, mprocess, buffer_size)
        env.process(plane.take_off(env, ground_start, ground_end, last_node, plane_speed, simulation_starttime))
        last_node = plane
        planes.append(plane)
        yield env.timeout(mplane)

def clock(env: simpy.Environment, interarrival: float, simulation_starttime: float):
    yield env.timeout(simulation_starttime)
    while True:
        yield env.timeout(interarrival)
        log(env, end="\r")

# t: simulation time
# mplane: plane take off interarrival
# mpacket: packet creation (per plane) interarrival
# mprocess: packet process (per plane) delay
# buffer_size: packet buffer size (per plane)
# distance: plane route distance
# ptransmission: success chance of a packet at 200km distance
def simulation(simulation_starttime=4*H, t=0.2*SEC, mplane=15*MIN, mpacket=100*MCS, mprocess=0.15*MCS, buffer_size=100, plane_speed=1500*KM/H, distance=6000*KM, ptransmissionAT200=0.9995):
    Plane.set_gamma(ptransmissionAT200)

    env = simpy.Environment()
    env.process(plane_generator(env, mplane, mpacket, mprocess, buffer_size, plane_speed, distance, simulation_starttime))
    env.process(clock(env, 10*MS, simulation_starttime))
    env.run(until=simulation_starttime + t)

    print("-- Simulation Complete --")
    if Packet.created == 0:
        print("No packets were created")
        return
    print(f"Success Ratio\t{Packet.created - Packet.dropped_buffer - Packet.dropped_transmission}/{Packet.created} ({(Packet.created - Packet.dropped_buffer - Packet.dropped_transmission)/Packet.created*100:.2f}%)")
    if Packet.transfered == 0:
        print("No packets were transfered")
        return
    print(f"Avg. latency\t{Packet.total_delay / Packet.transfered /MS:5.4f}ms")
    print(f"Packets dropped:{Packet.dropped_buffer + Packet.dropped_transmission}")
    print(f"\t Due to buffer\t\t{Packet.dropped_buffer}\t({Packet.dropped_buffer/Packet.created*100:.2f}%)")
    print(f"\t Due to transmission\t{Packet.dropped_transmission}\t({Packet.dropped_transmission/Packet.created*100:.2f}%)")
    pass

simulation()

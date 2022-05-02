from struct import pack
from typing import Union
from simpy import Environment, Store
from numpy.random import exponential

from utils import *

class Packet:
    def __init__(self, plane: 'Plane', timestamp: float):
        plane.packet_counter += 1
        self.plane = plane
        self.packet_no = plane.packet_counter
        self.timestamp = timestamp
    def __repr__(self):
        return f"<Packet #{self.plane.id}/{self.packet_no}>\t"

class GroundStation:
    def __init__(self, id: string, distance: float):
        self.id = id
        self.distance = distance
    def __repr__(self):
        return f"<GroundStation {self.id}>\t"
    def get_distance(self, current_time: float):
        return self.distance

    def receive_packet(self, env: Environment, packet: Packet):
        log(env.now, f"{self} has received packet {packet}")

plane_counter = 0
class Plane:
    def __init__(self, mu_packet: int):
        global plane_counter
        plane_counter += 1
        self.id = plane_counter
        self.mu_packet = mu_packet
        self.packet_counter = 0
        self.packet_buffer_capacity = 10

    def receive_packet(self, env: Environment, packet: Packet):
        self.packet_buffer.put(packet)

    def process_packets(self, env: Environment):
        while True:
            packet = yield self.packet_buffer.get()
            yield env.timeout(exponential(50*MCS)) # packet process delay
            receiving_node = self.node_ahead if True else self.node_behind
            yield env.timeout(abs(self.get_distance(env.now) - receiving_node.get_distance(env.now))/(300000*KM/SEC)) # lightspeed delay
            receiving_node.receive_packet(env, packet)

    def generate_packets(self, env: Environment):
        while self.onAir: # stop once plane lands
            yield env.timeout(exponential(self.mu_packet))
            packet = Packet(self, env.now)
            self.packet_buffer.put(packet)
            log(env.now, f"{packet} created")
            break # todo remove

    def get_distance(self, current_time):
        return min(self.distance, (current_time-self.time_at_takeoff)*self.speed)

    def take_off(self, env: Environment, node_start: GroundStation, node_end: GroundStation, node_ahead: Union['Plane', GroundStation], speed = 1500*KM/H):
        self.onAir = True
        self.time_at_takeoff = env.now
        self.speed = speed
        self.distance = node_end.distance - node_start.distance
        # add plane to the network chain
        self.node_behind = node_start
        self.node_ahead = node_ahead
        if type(self.node_ahead) is Plane:
            self.node_ahead.node_behind = self

        log(env.now, f"{self.id} has taken off")
        self.packet_buffer = Store(env, capacity=self.packet_buffer_capacity)
        self.packet_generator = env.process(self.generate_packets(env))
        self.packet_processor = env.process(self.process_packets(env))

        yield env.timeout(self.distance/self.speed)

        # remove plane from the network chain
        if type(self.node_behind) is Plane:
            self.node_behind.node_ahead = node_end
        self.onAir = False
        log(env.now, f"{self.id} has landed")

from typing import Union
from simpy import Environment, Store
from numpy.random import exponential

from utils import *

class Packet:
    total_delay = 0
    transfered = 0
    created = 0
    dropped = 0

    def __init__(self, plane: 'Plane', timestamp: float):
        Packet.created += 1
        plane.packet_counter += 1
        self.plane = plane
        self.packet_no = plane.packet_counter
        self.timestamp = timestamp
    def __repr__(self):
        return f"Packet{self.plane.id}.{self.packet_no}\t"

class GroundStation:
    def __init__(self, id: string, distance: float):
        self.id = id
        self.distance = distance
    def __repr__(self):
        return f"GroundStation({self.id})\t"
    def get_distance(self, current_time: float):
        return self.distance

    def receive_packet(self, env: Environment, packet: Packet):
        Packet.transfered += 1
        Packet.total_delay += env.now - packet.timestamp
        #log(env, f"{packet} was received by {self}")

plane_counter = 0
class Plane:
    def __init__(self, mpacket: float, mprocess: float, buffer_size: int):
        global plane_counter
        plane_counter += 1
        self.id = plane_counter
        self.mpacket = mpacket
        self.mprocess = mprocess
        self.packet_buffer_capacity = buffer_size
        self.packet_counter = 0
    def __repr__(self):
        return f"Plane{self.id:02}"

    def receive_packet(self, env: Environment, packet: Packet):
        if len(self.packet_buffer.items) < self.packet_buffer.capacity:
            self.packet_buffer.put(packet)
        else:
            Packet.dropped += 1
            #log(env, f"{packet} dropped")

    def process_packets(self, env: Environment):
        while self.onAir or len(self.packet_buffer.items) > 0: # stop once plane lands
            packet = yield self.packet_buffer.get()
            yield env.timeout(exponential(self.mprocess)) # packet process delay
            receiving_node = self.node_behind if self.distance > 2*self.get_distance(env.now) else self.node_ahead
            yield env.timeout(abs(self.get_distance(env.now) - receiving_node.get_distance(env.now))/(LIGHT_SECOND/SEC)) # lightspeed delay
            receiving_node.receive_packet(env, packet)

    def generate_packets(self, env: Environment):
        while self.onAir: # stop once plane lands
            yield env.timeout(exponential(self.mpacket))
            packet = Packet(self, env.now)
            self.receive_packet(env, packet)
            #log(env, f"{packet} created")

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

        log(env, f"{self} has taken off")
        self.packet_buffer = Store(env, capacity=self.packet_buffer_capacity)
        self.packet_generator = env.process(self.generate_packets(env))
        self.packet_processor = env.process(self.process_packets(env))

        yield env.timeout(self.distance/self.speed)

        # remove plane from the network chain
        if type(self.node_behind) is Plane:
            self.node_behind.node_ahead = node_end
        self.onAir = False
        log(env, f"{self} has landed")

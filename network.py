from typing import Union
from simpy import Environment, Store
from numpy import power, abs, log as ln
from numpy.random import exponential, uniform

from utils import *

class Packet:
    total_delay = 0
    transfered = 0
    created = 0
    dropped_buffer = 0
    dropped_transmission = 0

    def __init__(self, plane: 'Plane'):
        Packet.created += 1
        plane.packet_counter += 1

        self.plane = plane
        self.packet_no = plane.packet_counter
        self.timestamp = plane.env.now
    def __repr__(self):
        return f"Packet{self.plane.id}.{self.packet_no}\t"
    
    def transmit(self, env, sender, receiver):
        yield env.timeout(Plane.lightspeed_delay(sender.calculate_distance(receiver))) # lightspeed delay
        if type(receiver) is GroundStation:
            Packet.transfered += 1
            Packet.total_delay += self.plane.env.now - self.timestamp
            return
        if len(receiver.packet_buffer.items) < receiver.packet_buffer.capacity:
            self.sender = sender
            receiver.packet_buffer.put(self)
        else:
            Packet.dropped_buffer += 1

class GroundStation:
    def __init__(self, id: string, distance: float):
        self.id = id
        self.distance = distance
    def __repr__(self):
        return f"GroundStation({self.id})\t"
    def get_distance(self):
        return self.distance

class Plane:
    created = 0

    # ptransmissionAT200km: packet transmission rate @200km
    # returns gamma for packet_transmission_ratio
    @staticmethod
    def set_gamma(ptransmissionAT200km, transmission_range=500*KM) -> None:
        Plane.gamma = ln(ptransmissionAT200km) / ln((transmission_range-200*KM)/transmission_range) #return ln(ptransmissionAT200km)/ln((500-200)/500)

    @staticmethod
    def ptransmission(km, transmission_range=500*KM) -> float:
        return power(abs(transmission_range-km)/transmission_range, Plane.gamma)

    @staticmethod
    def lightspeed_delay(km) -> float:
        return km / (LIGHT_SECOND/SEC)

    def __init__(self, mpacket: float, mprocess: float, buffer_size: int):
        Plane.created += 1
        self.id = Plane.created

        self.mpacket = mpacket
        self.mprocess = mprocess
        self.packet_buffer_capacity = buffer_size
        self.packet_counter = 0
    def __repr__(self):
        return f"Plane{self.id:02}"

    def process_packets(self, env: Environment):
        while self.onAir or len(self.packet_buffer.items) > 0: # stop once plane lands and all packets get processed
            packet = yield self.packet_buffer.get()
            yield env.timeout(exponential(self.mprocess)) # packet process delay

            receiving_node = None
            distance_receiving_node = 500*KM
            distance_ahead = self.calculate_distance(self.node_ahead)
            distance_behind = self.calculate_distance(self.node_behind)

            if packet.plane is self:
                if  self.distance < 2*self.get_distance() and distance_ahead < 500*KM :
                    receiving_node = self.node_ahead
                    distance_receiving_node = distance_ahead
                elif distance_behind < 500*KM:
                    receiving_node = self.node_behind
                    distance_receiving_node = distance_behind
                else:
                    log(env, f"{self} has no node to communicate")
            elif packet.sender is self.node_ahead:
                receiving_node = self.node_behind
                distance_receiving_node = distance_behind
            elif packet.sender is self.node_behind:
                receiving_node = self.node_ahead
                distance_receiving_node = distance_ahead
            else:
                log(env, f"{self} has no sender")

            # random packet loss due to transition issues
            if uniform() > Plane.ptransmission(distance_receiving_node):
                receiving_node = None

            if receiving_node is None:
                Packet.dropped_transmission += 1
                continue
            else:
                env.process(packet.transmit(env, self, receiving_node))

    def generate_packets(self, env: Environment, simulation_starttime: float):
        if simulation_starttime - env.now > 0:
            yield env.timeout(simulation_starttime - env.now)
        while self.onAir: # stop once plane lands
            yield env.timeout(exponential(self.mpacket))
            packet = Packet(self)
            env.process(packet.transmit(env, self, self))

    # where current plane is
    def get_distance(self):
        return min(self.distance, (self.env.now - self.time_at_takeoff)*self.speed)

    # distance between two nodes
    def calculate_distance(self, node: Union['Plane', 'GroundStation']):
        return abs(self.get_distance() - node.get_distance())

    def take_off(self, env: Environment, node_start: GroundStation, node_end: GroundStation, node_ahead: Union['Plane', GroundStation], speed: float, simulation_starttime = -1):
        self.onAir = True
        self.env = env
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
        self.packet_processor = env.process(self.process_packets(env))
        self.packet_generator = env.process(self.generate_packets(env, simulation_starttime))

        yield env.timeout(self.distance/self.speed)

        # remove plane from the network chain
        if type(self.node_behind) is Plane:
            self.node_behind.node_ahead = node_end
        self.onAir = False
        log(env, f"{self} has landed")

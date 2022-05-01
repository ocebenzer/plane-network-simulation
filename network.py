import simpy
from numpy.random import exponential

from utils import *

plane_counter = 0
class Plane:
    speed = 1500*KM/H
     # todo packet capacity as resource

    def __init__(self, mu_packet=20*SEC):
        global plane_counter
        plane_counter += 1
        self.id = plane_counter
        self.mu_packet = mu_packet

    def generate_packet(self):
        while True:
            yield exponential(self.mu_packet)

    def take_off(self, env: simpy.Environment, flight_distance: float, previous_node, next_node):
        self.distance_left = flight_distance
        if type(previous_node) is Plane:
            self.previous_node = previous_node
            self.next_node = next_node
            previous_node.next_node = self

        log(env, f"{self.id} has taken off")
        yield env.timeout(self.distance_left/self.speed)
        log(env, f"{self.id} has landed")

class GroundStation:
    pass
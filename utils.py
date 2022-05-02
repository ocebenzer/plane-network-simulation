import simpy
import string


H = 3600
MIN = 60
SEC = 1
MS = 1/1000
MCS = 1/1000000

KM = 1

def log(env: simpy.Environment, text: string = ""):
    timestamp = env.now
    hour = int(timestamp/H)
    minute = int(timestamp/MIN - hour*60)
    second = timestamp/SEC - hour*3600 - minute*60
    print(f"{hour:2d}h.{minute:02d}m.{second:07.04f}: {text}")

import simpy
import string


H = 1
MIN = 1/60
SEC = 1/3600
MS = 1/3600000
MCS = 1/3600000000

KM = 1

def log(env: simpy.Environment, text: string = ""):
    timestamp = env.now
    hour = int(timestamp)
    minute = int(timestamp*60 - hour*60)
    second = timestamp*3600 - hour*3600 - minute*60
    print(f"{hour:2d}h.{minute:02d}m.{second:07.04f}: {text}")

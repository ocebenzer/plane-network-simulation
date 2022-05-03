import simpy
import string


MCS = 1
MS = 1000*MCS
SEC = 1000*MS
MIN = 60*SEC
H = 60*MIN

KM = 1
LIGHT_SECOND = 300000*KM

def to_datetime(timestamp: int):
    hour = int(timestamp/H)
    minute = int((timestamp - hour*H)/MIN)
    second = int((timestamp - hour*H - minute*MIN)/SEC)
    ms = int((timestamp - hour*H - minute*MIN - second*SEC)/MS)
    return f"{hour:2}h.{minute:02}m.{second:02}s.{ms:04}"
def log(env: simpy.Environment, text: string = ""):
    print(f"{to_datetime(env.now)}: {text}")

import string


H = 1
MIN = 1/60
SEC = 1/3600
MS = 1/3600000
MCS = 1/3600000000

KM = 1

def log(timestamp: float, text: string):
    hour = int(timestamp)
    minute = int(timestamp*60 - hour*60)
    second = timestamp*3600 - hour*3600 - minute*60
    print(f"{hour:2d}H {minute:02d}M {second:07.04f}: {text}")

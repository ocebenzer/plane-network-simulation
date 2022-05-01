import string


H = 1
MIN = 1/60
SEC = 1/3600

KM = 1

def log(env, text: string):
    print(f"{env.now:6.3f}: {text}")
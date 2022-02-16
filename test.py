import pprint
import time

import pyupbit

f = open("upbit.txt")
lines = f.readlines()
ACCESS_KEY = lines[0].strip()
SECRET_KEY = lines[1].strip()
f.close()

TICKER = 'KRW-ONG'

# upbit class instance
upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)
print(upbit.get_balance())


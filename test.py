import pprint

import pyupbit

f = open("upbit.txt")
lines = f.readlines()
ACCESS_KEY = lines[0].strip()
SECRET_KEY = lines[1].strip()
f.close()

# # upbit class instance
# upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)
#
# resp = upbit.get_individual_order('8c67b3a4-33ac-475a-a181-42bf1c77db30')
#
# # pprint.pprint(resp)
# pprint.pprint(resp)
# print(resp['uuid'])

orderbook = pyupbit.get_orderbook('KRW-ONG')
pprint.pprint(orderbook)

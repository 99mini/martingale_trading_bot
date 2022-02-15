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
#
# resp = upbit.get_individual_order('8c67b3a4-33ac-475a-a181-42bf1c77db30')
order_list = upbit.get_order(ticker_or_uuid=TICKER)
for order in order_list:
    uuid = order['uuid']
    print(uuid)
    upbit.cancel_order(uuid=uuid)
pprint.pprint(order_list)
time.sleep(1)
amount = upbit.get_balance_t(ticker=TICKER)
print(amount)
upbit.sell_market_order(ticker=TICKER, volume=amount)
order_list = upbit.get_order(ticker_or_uuid=TICKER)
pprint.pprint(order_list)
# pprint.pprint(resp)
# print(resp['uuid'])


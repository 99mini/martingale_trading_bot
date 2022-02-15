import datetime
import time

import pyupbit

all_ticker_url = "https://api.upbit.com/v1/ticker"

# read upbit key
f = open("upbit.txt")
lines = f.readlines()
ACCESS_KEY = lines[0].strip()
SECRET_KEY = lines[1].strip()
f.close()

# upbit class instance
upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)


# 매수 주문
def buy_order(ticker, price, volume):
    try:
        resp = upbit.buy_limit_order(ticker=ticker,
                                     price=price,
                                     volume=volume)
        time.sleep(1)
        return resp['uuid']

    except Exception as e:
        print("buy_order", e)


# 매도 주문
def sell_order(ticker, price, volume):
    try:
        resp = upbit.sell_limit_order(ticker=ticker,
                                      price=price,
                                      volume=volume)
        time.sleep(1)

        return resp['uuid']

    except Exception as e:
        print("sell_order", e)


'''
초기설정
1. 트레이딩할 코인 설정
2. 1회 주문 자금
3. 트레이딩 상단가 / 하단가 설정 (박스권을 설정)
4. 목표 인터벌 설정 (호가 단위)

프로그램 시작
1. 프로그램 시작 시 현재 가격을 (기준)으로 삼고 지정가 매수 주문
2. 주문과 동시에 (기준 + 목표 인터벌) 가격에 지정가 매도
3-1. 매도가 체결되면 그 가격에 다시 매수 | 기준 = 기준
3-2. 매도가 체결되지 않고 가격이 하락한다면 (기준 - 목표 인터벌) 가격에 지정가 매수 주문 | 기준 -= 목표 인터벌
4. 상기 2번으로 회기
'''

# init setting
TICKER = 'KRW-ONG'
ONE_ORDER_AMOUNT = 5_050
TOP = 1250
BOTTOM = 1000
INTERVAL = 10
TICK = 5

cur_price = pyupbit.get_current_price(ticker=TICKER)
base_price = cur_price - INTERVAL
order_volume = ONE_ORDER_AMOUNT / cur_price
sell_order_uuid_list = set()

buy_uuid = buy_order(ticker=TICKER,
                     price=cur_price,
                     volume=order_volume)
if not upbit.get_individual_order(buy_uuid)['trades']:
    print('not init buy......')
    time.sleep(10)
    # 매수 취소 후 exit
    upbit.cancel_order(buy_uuid)
    exit()

sell_order_uuid_list.add(sell_order(ticker=TICKER,
                                    price=cur_price + INTERVAL,
                                    volume=order_volume))
print(*sell_order_uuid_list)
print("#" * 100)
print("매수: {0}".format(cur_price))
print("예약 매도: {0}".format(cur_price + INTERVAL))
print("수량: {0}".format(order_volume))
print("목표가: {0}".format(base_price))
print("#" * 100)

while True:
    try:
        cur_price = pyupbit.get_current_price(ticker=TICKER)

        # 프로그램 종료
        if cur_price > TOP or cur_price < BOTTOM:
            break

        # 기준가 도달시 매수와 예약 매도 실행
        if base_price == cur_price:
            time.sleep(1)
            # 구매 주문
            buy_uuid = buy_order(ticker=TICKER,
                                 price=cur_price,
                                 volume=order_volume)

            # 구매가 안되었을 경우 기다린다
            if not upbit.get_individual_order(buy_uuid)['trades']:
                print('not init buy......')
                time.sleep(10)
                # 매수 취소 후 continue
                upbit.cancel_order(buy_uuid)
                continue

            # 예약 매도 주문
            sell_order_uuid_list.add(sell_order(ticker=TICKER,
                                                price=cur_price + INTERVAL,
                                                volume=order_volume))

            base_price -= INTERVAL
            print("매수: {0}".format(cur_price))
            print("예약 매도: {0}".format(cur_price + INTERVAL))
            print("수량: {0}".format(order_volume))
            print("목표가: {0}".format(base_price))
            print("#" * 100)

        # 미채결 물량이 있는 경우
        # TODO main error... Set changed size during iteration
        for uuid in sell_order_uuid_list:
            resp = upbit.get_individual_order(uuid)
            # 체결이 된 경우
            # 같은 가격에 매수를 진행하고
            # 기준가를 다시 설정한다.
            if resp is not None and len(resp['trades']) > 0:
                sell_price = float(resp['trades'][0]['price'])
                sell_order_uuid_list.remove(resp['uuid'])

                time.sleep(1)
                # 구매 주문
                buy_uuid = buy_order(ticker=TICKER,
                                     price=sell_price,
                                     volume=order_volume)

                # 구매가 안되었을 경우 기다린다
                if not upbit.get_individual_order(buy_uuid)['trades']:
                    print('not init buy......')
                    time.sleep(10)
                    # 매수 취소 후 continue
                    upbit.cancel_order(buy_uuid)
                    continue

                # 예약 매도 주문
                sell_order_uuid_list.add(sell_order(ticker=TICKER,
                                                    price=sell_price + INTERVAL,
                                                    volume=order_volume))
                base_price = sell_price - INTERVAL

                print("\n매도 체결: {0}".format(sell_price))
                print("기준 가격 갱신: {0}".format(base_price))
                print("#" * 100)
                print("\n매수: {0}".format(cur_price))
                print("예약 매도: {0}".format(cur_price + INTERVAL))
                print("수량: {0}".format(order_volume))
                print("#" * 100)

        if datetime.datetime.now().second % 10 == 0:
            print("=" * 100)
            print("기준 가격: {0}".format(base_price))
            print("현재 가격: {0}".format(cur_price))
            print("목표 인터벌: {0}".format(INTERVAL))

            print("=" * 45 + '미채결물량' + "=" * 45)
            for uuid in sell_order_uuid_list:
                resp = upbit.get_individual_order(uuid)
                sell_price = float(resp['price'])
                print(sell_price)
            print("=" * 100)
        time.sleep(1)
    except Exception as e:
        print("main error...", e)

# 프로그램 종료시 전량 매도
for uuid in sell_order_uuid_list:
    upbit.cancel_order(uuid)
amount = upbit.get_amount(ticker=TICKER)
upbit.sell_market_order(ticker=TICKER, volume=amount)
print("전량 매도")
print("프로그램 종료")

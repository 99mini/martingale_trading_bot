import datetime
import time

import pyupbit
import requests

from config import *

all_ticker_url = "https://api.upbit.com/v1/ticker"

# read upbit key
f = open("upbit.txt")
lines = f.readlines()
ACCESS_KEY = lines[0].strip()
SECRET_KEY = lines[1].strip()
f.close()

# upbit class instance
upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)

# 텔레그램 메세지 보내기
def telegramMassageBot(msg):
    params = {'chat_id': telebotid, 'text': msg}
    # 텔레그램으로 메시지 전송
    try:
        requests.get(teleurl, params=params)
    except Exception as e:
        print('telegram error: ', e)


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

def exec_exit():
    # 미채결 주문 취소
    order_list = upbit.get_order(ticker_or_uuid=TICKER)
    for order in order_list:
        uuid = order['uuid']
        print(uuid)
        upbit.cancel_order(uuid=uuid)
    time.sleep(1)
    # 전량 매도
    amount = upbit.get_balance_t(ticker=TICKER)
    upbit.sell_market_order(ticker=TICKER, volume=amount)
    order_list = upbit.get_order(ticker_or_uuid=TICKER)
    # 텔레그렘 메세지
    msg = '체널이탈로 인한 종료'
    telegramMassageBot(msg=msg)
    print("전량 매도")
    print("프로그램 종료")
    exit(0)


def init_setting():
    # 보유 현금 잔고
    krw_balance = upbit.get_balance()
    print("보유 현금 잔고: ", krw_balance)

    cur_price = pyupbit.get_current_price(ticker=TICKER) + TICK
    base_price = cur_price
    order_volume = ONE_ORDER_AMOUNT / cur_price
    buy_uuid = buy_order(ticker=TICKER,
                         price=cur_price,
                         volume=order_volume)
    if not upbit.get_individual_order(buy_uuid)['trades']:
        print('not init buy......')
        time.sleep(10)
        # 매수 취소 후 exit
        upbit.cancel_order(buy_uuid)
        exit()
    sell_order(ticker=TICKER,
               price=cur_price + INTERVAL,
               volume=order_volume)
    print("#" * 100)
    print("매수: {0}".format(cur_price))
    print("예약 매도: {0}".format(cur_price + INTERVAL))
    print("수량: {0}".format(order_volume))
    print("목표가: {0} | {1}".format(base_price - INTERVAL, base_price + INTERVAL))
    print("#" * 100)

    return base_price

'''
초기설정
1. 트레이딩할 코인 설정
2. 1회 주문 자금 (1회 주문 자금은 보유 자산의 최소 1/20 씩 들어가야 된다.)
3. 트레이딩 상단가 / 하단가 설정 (박스권을 설정)
4. 목표 인터벌 설정 (호가 단위)
5. 코인의 틱 단위 설정

프로그램 시작
1. 프로그램 시작 시 현재 가격을 (기준)으로 삼고 지정가 매수 주문
2. 주문과 동시에 (기준 + 목표 인터벌) 가격에 지정가 매도
3-1. 매도가 체결되면 그 가격에 다시 매수 | 기준 = 기준
3-2. 매도가 체결되지 않고 가격이 하락한다면 (기준 - 목표 인터벌) 가격에 지정가 매수 주문 | 기준 -= 목표 인터벌
4. 상기 2번으로 회기
'''

# init setting
# 거래 코인
TICKER = 'KRW-SAND'
# 1회 매수 금액
ONE_ORDER_AMOUNT = 5_050
# 프로그램 밴딩 상단
TOP = 5800
# 프로그램 밴딩 하단
BOTTOM = 4500
# 거래 간격
INTERVAL = 30
# 거래 코인 1틱 가격
TICK = 5


base_price = init_setting()

while True:
    try:
        cur_price = pyupbit.get_current_price(ticker=TICKER)
        krw_balance = upbit.get_balance()

        # 보유 현금이 1회 주문 금액 보다 작아지면 지나간다.
        if krw_balance < ONE_ORDER_AMOUNT:
            continue
        # 프로그램 종료
        if cur_price > TOP or cur_price < BOTTOM:
            exec_exit()

        # 기준가 도달시 매수와 예약 매도 실행
        # 가격 하락시 매수
        if base_price - INTERVAL == cur_price + TICK or base_price + INTERVAL == cur_price + TICK:
            order_volume = ONE_ORDER_AMOUNT / cur_price
            time.sleep(1)
            # 구매 주문
            # 하락시
            if base_price - INTERVAL == cur_price + TICK:
                order_price = base_price - INTERVAL
            # 상승시
            else:
                order_price = base_price + INTERVAL
            buy_uuid = buy_order(ticker=TICKER,
                                 price=order_price,
                                 volume=order_volume)

            # 구매가 안되었을 경우 기다린다
            if not upbit.get_individual_order(buy_uuid)['trades']:
                print('not init buy......')
                time.sleep(10)
                # 매수 취소 후 continue
                upbit.cancel_order(buy_uuid)
                continue

            # 예약 매도 주문
            sell_order(ticker=TICKER,
                       price=order_price + INTERVAL,
                       volume=order_volume)

            base_price = order_price
            print("매수: {0}".format(cur_price))
            print("예약 매도: {0}".format(cur_price + INTERVAL))
            print("수량: {0}".format(order_volume))
            print("목표가: {0} | {1}".format(base_price - INTERVAL, base_price + INTERVAL))
            print("#" * 100)

        if datetime.datetime.now().second % 10 == 0:
            print("=" * 100)
            print(datetime.datetime.now())
            print("현금 잔고: {0}".format(krw_balance))
            print("기준 가격: {0}".format(base_price))
            print("현재 가격: {0}".format(cur_price))
            print("목표가: {0} | {1}".format(base_price - INTERVAL, base_price + INTERVAL))
            print("목표 인터벌: {0}".format(INTERVAL))

        time.sleep(1)
    except Exception as e:
        print("main error...", e)

import datetime
import time

import pyupbit
import requests

from config import *
from constants import *


class MartingaleBot:
    def __init__(self):
        # read upbit key
        f = open("upbit.txt")
        lines = f.readlines()
        ACCESS_KEY = lines[0].strip()
        SECRET_KEY = lines[1].strip()
        f.close()

        # upbit class instance
        self.upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)
        self._init_setting()

    def exec_martingale_bot(self):
        cur_price = pyupbit.get_current_price(ticker=TICKER)
        krw_balance = self.upbit.get_balance()

        # 프로그램 종료
        if cur_price > TOP or cur_price < BOTTOM:
            self._exec_exit()

        # 보유 현금이 1회 주문 금액 보다 작아지면 지나간다.
        if krw_balance < ONE_ORDER_AMOUNT:
            self._base_price = cur_price
            return

        # 목표가를 지나쳐 간 경우
        if self._base_price - INTERVAL < cur_price or self._base_price + INTERVAL > cur_price:
            self._order_logic(cur_price)

        # 기준가 도달시 매수와 예약 매도 실행
        # 가격 하락시 매수
        if self._base_price - INTERVAL == cur_price or self._base_price + INTERVAL == cur_price:
            self._order_logic(cur_price)

            print("매수: {0}".format(cur_price))
            print("예약 매도: {0}".format(cur_price + INTERVAL))
            print("목표가: {0} | {1}".format(self._base_price - INTERVAL, self._base_price + INTERVAL))
            print("#" * 100)

        if datetime.datetime.now().second % 10 == 0:
            print("=" * 100)
            print(datetime.datetime.now())
            print("현금 잔고: {0}".format(krw_balance))
            print("기준 가격: {0}".format(self._base_price))
            print("현재 가격: {0}".format(cur_price))
            print("목표가: {0} | {1}".format(self._base_price - INTERVAL, self._base_price + INTERVAL))
            print("목표 인터벌: {0}".format(INTERVAL))

    # 텔레그램 메세지 보내기
    def _telegramMassageBot(self, msg):
        params = {'chat_id': telebotid, 'text': msg}
        # 텔레그램으로 메시지 전송
        try:
            requests.get(teleurl, params=params)
        except Exception as e:
            print('telegram error: ', e)

    # 주문 로직
    def _order_logic(self, cur_price):

        # 예약 매도가 이미 있는 경우 return
        if self._check_wait_order(cur_price + INTERVAL):
            return

        order_volume = ONE_ORDER_AMOUNT / cur_price
        time.sleep(1)
        # 구매 주문
        # 하락시
        if self._base_price - INTERVAL == cur_price:
            order_price = self._base_price - INTERVAL
        # 상승시
        else:
            order_price = self._base_price + INTERVAL
        buy_uuid = self._buy_order(ticker=TICKER,
                                   price=order_price,
                                   volume=order_volume)

        # 구매가 안되었을 경우 기다린다
        if not self.upbit.get_individual_order(buy_uuid)['trades']:
            print('not init buy......')
            time.sleep(3)
            resp = self.upbit.cancel_order(buy_uuid)
            # 매수 취소가 수행되었으면 리턴
            if resp is not None:
                return

            # 예약 매도 주문
        self._sell_order(ticker=TICKER,
                         price=order_price + INTERVAL,
                         volume=order_volume)

        self._base_price = order_price

    # 매수 주문
    def _buy_order(self, ticker, price, volume):
        try:
            resp = self.upbit.buy_limit_order(ticker=ticker,
                                              price=price,
                                              volume=volume)
            time.sleep(1)
            return resp['uuid']

        except Exception as e:
            print("buy_order", e)

    # 매도 주문
    def _sell_order(self, ticker, price, volume):
        try:
            resp = self.upbit.sell_limit_order(ticker=ticker,
                                               price=price,
                                               volume=volume)
            time.sleep(1)

            return resp['uuid']

        except Exception as e:
            print("sell_order", e)

    # 예약 매도 확인하기
    def _check_wait_order(self, price):
        wait_orders = self.upbit.get_order(ticker_or_uuid=TICKER)
        price = str(float(price))
        for order in wait_orders:
            if price == order['price']:
                return True

    def _exec_exit(self):
        # 미채결 주문 취소
        order_list = self.upbit.get_order(ticker_or_uuid=TICKER)
        for order in order_list:
            uuid = order['uuid']
            self.upbit.cancel_order(uuid=uuid)
        time.sleep(1)
        # 전량 매도
        amount = self.upbit.get_balance_t(ticker=TICKER)
        self.upbit.sell_market_order(ticker=TICKER, volume=amount)

        final_krw = self.upbit.get_balance()

        # 텔레그렘 메세지
        msg = '체널이탈로 인한 종료\n초기 자금: {0}\n기말 자금: {1}\n수익률: {2}'\
            .format(self.init_krw, final_krw, (final_krw-self.init_krw)/self.init_krw * 100)
        self._telegramMassageBot(msg=msg)
        print("전량 매도")
        print("프로그램 종료")
        exit(0)

    def _init_setting(self):
        # 보유 현금 잔고
        self.init_krw = krw_balance = self.upbit.get_balance()
        print("보유 현금 잔고: ", krw_balance)

        # 한 틱 높게 구매
        cur_price = pyupbit.get_current_price(ticker=TICKER) + TICK
        self._base_price = cur_price
        order_volume = ONE_ORDER_AMOUNT / cur_price

        # 이미 보유 코인이 있는 경우
        amount = self.upbit.get_balance_t(ticker=TICKER)
        if amount * ONE_ORDER_AMOUNT > ONE_ORDER_AMOUNT:
            pass

        elif krw_balance > ONE_ORDER_AMOUNT:
            buy_uuid = self._buy_order(ticker=TICKER,
                                       price=cur_price,
                                       volume=order_volume)
            if not self.upbit.get_individual_order(buy_uuid)['trades']:
                print('not init buy......')
                time.sleep(5)
                resp = self.upbit.cancel_order(buy_uuid)
                # 매수 취소가 진행되면 종료
                if resp is not None:
                    exit(0)
            self._sell_order(ticker=TICKER,
                             price=cur_price + INTERVAL,
                             volume=order_volume)
            print("#" * 100)
            print("매수: {0}".format(cur_price))
            print("예약 매도: {0}".format(cur_price + INTERVAL))
            print("수량: {0}".format(order_volume))
            print("목표가: {0} | {1}".format(self._base_price - INTERVAL, self._base_price + INTERVAL))
            print("#" * 100)

        msg = "upbit martingale start\n거래 코인: {0}\n초기 자금: {1}".format(TICKER, krw_balance)
        self._telegramMassageBot(msg)

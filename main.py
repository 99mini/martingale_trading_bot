import time
from martingale_bot import MartingaleBot

all_ticker_url = "https://api.upbit.com/v1/ticker"

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

martingale_bot = MartingaleBot()

while True:
    try:
        martingale_bot.exec_martingale_bot()

        time.sleep(1)
    except Exception as e:
        print("main error...", e)

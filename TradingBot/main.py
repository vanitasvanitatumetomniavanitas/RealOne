# bot.py
import time
from config import API_KEY, SECRET_KEY, PASSPHRASE, SYMBOL, BAR_INTERVAL, LEVERAGE, TRADE_AMOUNT
from logger import setup_logger
from indicator import calculate_macd
from exchange_client import ExchangeClient
from datetime import datetime, timezone, timedelta

# 로거 설정
logger = setup_logger()


class OKXTradingBot:

    def __init__(self, exchange_client):
        # 거래소 클라이언트 객체를 초기화합니다.
        self.exchange_client = exchange_client
        # 현재 포지션 상태를 초기화 (롱 또는 숏)합니다.
        self.position_side = None

    def main(self):
        while True:
            try:
                # 켄들 데이터 가져오기 (최근 10,000개 켄들)
                df = self.exchange_client.get_candle_data(BAR_INTERVAL)
                # MACD 지표 계산 (12, 26, 9 기본 설정 사용)
                df = calculate_macd(df)

                # 현재 및 이전 켄들의 MACD 값 가져오기
                current_macd = df['MACD'].iloc[-1]  # 가장 최근 켄들의 MACD
                previous_macd = df['MACD'].iloc[-2]  # 이전 켄들의 MACD
                # 현재 거래 추어의 가격 가져오기
                price = self.exchange_client.get_current_price()

                # 거래 크기 계산 (고정 거래 금액 기준)
                # 레버리지 적용 없이 TRADE_AMOUNT만 사용
                leveraged_amount = TRADE_AMOUNT * LEVERAGE
                size = leveraged_amount / price

                # MACD 교차를 이용한 매매 신호 확인
                if previous_macd < 0 and current_macd > 0:
                    # MACD가 음수에서 양수로 교차할 때 매수 신호 발생
                    signal = 'buy'
                elif previous_macd > 0 and current_macd < 0:
                    # MACD가 양수에서 음수로 교차할 때 매도 신호 발생
                    signal = 'sell'
                else:
                    # 교차가 없는 경우 매매 신호 없음
                    signal = None

                # 매매 신호에 따라 포지션 관리
                if signal == 'buy' and self.position_side != 'long':
                    # 매수 신호가 발생하고 현재 포지션이 롱이 아니는 경우
                    logger.info(f"롱 포지션 진입 신호 발생. 현재 MACD: {current_macd}")
                    # 매수 주문 실행
                    self.exchange_client.place_order('buy', size)
                    # 주문 성공 시 로그 기록
                    logger.info(f"롱 포지션 진입 주문 실행. 사이즈: {size}")
                    # 현재 포지션을 롱으로 설정
                    self.position_side = 'long'

                elif signal == 'sell' and self.position_side != 'short':
                    # 매도 신호가 발생하고 현재 포지션이 숏이 아니는 경우
                    logger.info(f"숏 포지션 진입 신호 발생. 현재 MACD: {current_macd}")
                    # 매도 주문 실행
                    self.exchange_client.place_order('sell', size)
                    # 주문 성공 시 로그 기록
                    logger.info(f"숏 포지션 진입 주문 실행. 사이즈: {size}")
                    # 현재 포지션을 숏으로 설정
                    self.position_side = 'short'

                # 현재 시간 및 상태 로그
                now = datetime.now(timezone.utc) + timedelta(
                    hours=9)  # UTC+9 한국 시간
                logger.info(
                    f"[코드 실행 중] 현재 MACD: {current_macd}, 현재 가격: {price}")

                # 다음 30분 봉까지 대기
                # 현재 시간의 번과 소를 계산하여 다음 30분 봉까지 남은 시간을 계산
                sleep_seconds = 1800 - (now.minute % 30) * 60 - now.second
                time.sleep(sleep_seconds)

            except Exception as e:
                # 오류 발생 시 오류 로그 기록
                logger.error(f"오류 발생: {e}")


if __name__ == "__main__":
    # 거래소 클라이언트 객체 생성
    exchange_client = ExchangeClient(API_KEY, SECRET_KEY, PASSPHRASE, SYMBOL,
                                     LEVERAGE)
    # 거래 벌 인스턴스 생성 및 메인 로직 실행
    bot = OKXTradingBot(exchange_client)
    bot.main()

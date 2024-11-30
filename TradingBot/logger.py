# logger.py
import logging
from datetime import datetime, timezone, timedelta


class CustomFormatter(logging.Formatter):

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created,
                                    tz=timezone.utc) + timedelta(hours=9)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()


def setup_logger():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[
                            logging.FileHandler('okx_trading_bot.log'),
                            logging.StreamHandler()
                        ])

    formatter = CustomFormatter('%(asctime)s [%(levelname)s] %(message)s')
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    return logging.getLogger()

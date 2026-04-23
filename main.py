import ccxt
from datetime import datetime, timedelta
import pandas as pd
from colors import color, ColorPrint, Colors


class PriceFetcher:
    '''
    Класс для получения цен криптовалют с бирж и сохранения данных.

    На вход нужно подавать объект класса ccxt

    Пример:
        import ccxt
        
        # Способ 1: Объекты бирж
        fetcher = PriceFetcher([ccxt.binance(), ccxt.bybit()])
        
        # Способ 2: через класс Exchanges
        exch = Exchanges()
        exchanges = exch.exchanges_convert(['binance', 'bybit'])
        fetcher = PriceFetcher(exchanges)
    
    Note:
        Не передавайте строки! Только объекты бирж.
    '''

    def __init__(self, exchange_obj: list = None):

            self.exchanges: list = exchange_obj if exchange_obj else []

    def get_ticker(self, symbols: list, exchanges: list = None ) -> tuple[list, list]:
        '''
        Получение текущих цен для указанных торговых пар со заданных бирж.

        Args:
            symbols (list): Список торговых пар.
                Пример: ['BTC/USD', 'ETH/USD', 'SOL/USD']
            exchanges (list, optional): Список объектов бирж CCXT.
                Если None (по умолчанию), использует биржи, переданные в конструктор.
                Если передан, временно использует эти биржи.
        '''
        success_data = []
        error_data = []

        target_exchanges = exchanges if exchanges is not None else self.exchanges

        if not target_exchanges:
            color.error(f'[ERROR] Не переданы биржи! Укажите их в конструкторе или в методе get_ticker()')
            return [], []
        
        # Перебираем все биржи из списка
        for exchange in target_exchanges:
            
            # Перебираем все торговые пары
            for symbol in symbols:

                try:

                    # Пытаемся получить тикер (текущие цены) с биржи
                    ticker = exchange.fetch_ticker(symbol)
                    success_data.append(
                        {
                            "exchange": exchange.name,
                            "symbol": ticker.get("symbol", None),
                            "bid": ticker.get("bid", None),
                            "ask": ticker.get("ask", None),
                            "last": ticker.get("last", None),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

                except Exception as ex:

                    color.error(f"[ERROR] Ошибка получения данных с биржи {exchange.name}, на паре {symbol}")
                    color.error(f'[ERROR] {ex}')
                    error_data.append(
                        {
                            "exchange": exchange.name,
                            "symbol": symbol,
                            "error": str(ex),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

        return success_data, error_data

    def get_ohlcv(self,
                symbols: list,
                exchanges: list = None,
                timeframe: str = '1h',
                days_back: int = 7,) -> tuple[list, list]:

        limit_per_request = 200
        success_data = []
        err_data = []

        target_exchanges = exchanges if exchanges is not None else self.exchanges

        if not target_exchanges:
            color.error(f'[ERROR] Не переданы биржи! Укажите их в конструкторе или в методе get_ohlcv()')
            return ([], [])
        
        since_dt = datetime.now() - timedelta(days=days_back)
        since_ms = int(since_dt.timestamp() * 1000)

        total_symbols = len(target_exchanges) + len(symbols)
        completed = 0
        
        for exchange in target_exchanges:
            if not exchange.has['fetchOHLCV']:
                err_data.append({
                        'exchange': exchange.name,
                        'timeframe': timeframe,
                        'error': 'Биржа не поддерживает fetchOHLCV',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                continue

            for symbol in symbols:

                completed += 1
                color.info(f'[INFO] Прогресс {completed}/{total_symbols}')

                all_candles = []
                current_since = since_ms

                try:
                    while True:

                        ohlcv_data = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=current_since, limit=limit_per_request)

                        if not ohlcv_data:
                            break

                        all_candles.extend(ohlcv_data)

                        if len(ohlcv_data) < limit_per_request:
                            break

                        current_since = ohlcv_data[-1][0] + 1

                    success_data.append({
                        'exchange': exchange.name,
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'columns_data': ['timestamp', 'open', 'high', 'low', 'close', 'volume'],  # Список свечей
                        'data': all_candles,
                        'candles_count': len(all_candles),
                        'days_back': days_back,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })

                    color.success(f"[SUCCESS] {exchange.name} {symbol}: {len(all_candles)} свечей")


                except Exception as ex:
                    color.error(f"[ERROR] Ошибка получения данных свеч с биржи {exchange.name}, на паре {symbol}")
                    color.error(f'[ERROR] {ex}')
                    err_data.append({
                        'exchange': exchange.name,
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'error': str(ex),
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })

        return success_data, err_data

class Exchanges:
    '''
    Класс для управления списком криптовалютных бирж.
    Позволяет проверять поддержку бирж и создавать их экземпляры.
    '''

    def __init__(self):
        self.all_exchanges = ccxt.exchanges

    def exchanges_convert(self, user_exchanges: list, enable_rate_limit: bool = True) -> list:
        '''
        Преобразует список названий бирж в список объектов CCXT.
        Проверяет, поддерживается ли каждая биржа.

        Args:
            user_exchanges (list): Список названий бирж.
                Пример: ['binance', 'bybit', 'okx', 'kucoin', 'coinbase']
            enable_rate_limit (bool, optional): Включить защиту от частых запросов.
                По умолчанию True. Рекомендуется оставлять включенным для избежания бана.
        '''

        if not user_exchanges:
            color.error(f"[ERROR] Вы не передали список используемых бирж")
            return []

        exchange_instances = []

        for user_exchange in user_exchanges:

            if user_exchange in self.all_exchanges:

                exchange_class = getattr(ccxt, user_exchange)
                exchange_instances.append(exchange_class({
                    'enableRateLimit': enable_rate_limit
                }))

                color.success(f"[SUCCESS] {user_exchange} Поддерживается")

            else:
                color.error(f"[ERROR] {user_exchange} Не поддерживается")

        return exchange_instances

    def get_supported_exchanges_obj(self, show: bool = False, limit: int = None, enable_rate_limit: bool = True) -> list:
        """
        Возвращает список объектов всех поддерживаемых бирж CCXT.
            
        Args:
            show (bool, optional): Если True, выводит список в консоль.
                По умолчанию False.
            limit (int, optional): Максимальное количество возвращаемых объектов.
                Если None (по умолчанию), возвращает все объекты.
                Пример: limit=5 вернет первые 5 бирж.
            enable_rate_limit (bool, optional): Включить защиту от частых запросов.
                По умолчанию True. Рекомендуется оставлять включенным для избежания бана.
        """
        if show:
            print(self.all_exchanges)
    
        # СОЗДАНИЕ ОБЪЕКТОВ БИРЖ
        exchanges_obj = []

        for exchange_name in self.all_exchanges:
            if limit is not None and len(exchanges_obj) >= limit: 
                return exchanges_obj
                
            try:
                exchange_class = getattr(ccxt, exchange_name)
                exchanges_obj.append(exchange_class({
                    'enableRateLimit': enable_rate_limit
                }))
            except Exception as ex:
                color.error(f'[ERROR] Не удалось создать объект {exchange_name}: {ex}')

        return exchanges_obj

    def get_supported_exchanges_str(self, show: bool = False, limit: int = None) -> list:
        """
        Возвращает список названий всех поддерживаемых бирж CCXT.
            
        Args:
            show (bool, optional): Если True, выводит список в консоль.
                По умолчанию True.
            limit (int, optional): Максимальное количество возвращаемых объектов.
                Если None (по умолчанию), возвращает все объекты.
                Пример: limit=5 вернет первые 5 бирж.
        """
        if show:
            print(self.all_exchanges)

        if limit is not None: 
            return self.all_exchanges[:limit]

        return self.all_exchanges




import ccxt
from datetime import datetime, timedelta
import pandas as pd
from colors import color, ColorPrint, Colors


class CryptoDataFetcher:
    """
    Получает данные с криптовалютных бирж.
    
    Этот класс отвечает за получение OHLCV данных (Open, High, Low, Close, Volume)
    с нескольких бирж с поддержкой пагинации для обхода лимитов.
    
    Пример:
        fetcher = CryptoDataFetcher(exchange_instances)
        data, errors = fetcher.fetch_ohlcv(['BTC/USDT'], timeframe='1h', days_back=7)
    """

    def __init__(self, exchange_obj: list = None):

            self.exchanges: list = exchange_obj if exchange_obj else []

    def fetch_tickers(self, symbols: list, exchanges: list[pd.DataFrame] = None, show: bool = False) -> tuple[list, list]:
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

    def fetch_ohlcv(self,
                symbols: list,
                show: bool = False,
                exchanges: list = None,
                timeframe: str = '1h',
                days_back: int = 7,) -> tuple[list, list]:
        """
        Получает OHLCV данные для указанных торговых пар и бирж.
        
        Этот метод реализует пагинацию для обхода лимитов бирж,
        делая несколько запросов по 200 свечей за раз.
        
        Args:
            symbols: Список торговых пар (например, ['BTC/USDT', 'ETH/USDT'])
            exchanges: Список объектов бирж (если None, использует self.exchanges)
            timeframe: Таймфрейм свечей ('1m', '5m', '1h', '4h', '1d')
            days_back: Количество дней назад (по умолчанию 7)
        
        Returns:
            tuple: (success_data, error_data)
                - success_data: Список словарей с OHLCV данными
                - error_data: Список словарей с информацией об ошибках
        
        Пример:
            fetcher = CryptoDataFetcher(exchanges)
            data, errors = fetcher.fetch_ohlcv(['BTC/USDT'], timeframe='1h', days_back=7)
        """
        limit_per_request = 200
        success_data = []
        err_data = []

        target_exchanges = exchanges if exchanges is not None else self.exchanges

        if not target_exchanges:
            color.error(f'[ERROR] Не переданы биржи! Укажите их в конструкторе или в методе get_ohlcv()')
            return ([], [])
        
        since_dt = datetime.now() - timedelta(days=days_back)
        since_ms = int(since_dt.timestamp() * 1000)

        total_symbols = len(target_exchanges) * len(symbols)
        completed = 0
        
        for exchange in target_exchanges:
            if not exchange.has.get('fetchOHLCV', False):
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

                        ohlcv_data = exchange.fetch_ohlcv(symbol=symbol,
                                                          timeframe=timeframe,
                                                          since=current_since,
                                                          limit=limit_per_request)

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
        if show:
            color.info(f'[INFO] Успешно собрано {len(success_data)} данных свечей')
            color.info(f'[INFO] Не успешных {len(err_data)}')
        return success_data, err_data

class ExchangeManager:
    """
    Управление криптовалютными биржами через библиотеку CCXT.
    
    Этот класс отвечает за создание и управление объектами бирж
    из библиотеки CCXT. Позволяет конвертировать названия бирж
    в рабочие объекты для дальнейшего получения данных.
    
    Пример:
        manager = ExchangeManager()
        exchanges = manager.create_instances(['binance', 'bybit', 'okx'])
    """

    def __init__(self):
        self.exchanges_name = ccxt.exchanges
        self.exchanges_instances = None

    def create_instances(self,
                         user_exchanges: list[str],
                         enable_rate_limit: bool = True,
                         show: bool = False) -> list:
        """
        Преобразует список названий бирж в список объектов CCXT.
        
        Args:
            user_exchanges: Список строк с названиями бирж (например, ['binance', 'bybit'])
            enable_rate_limit: Включить защиту от частых запросов (рекомендуется True)
        
        Returns:
            list: Список объектов бирж CCXT, готовых к использованию
        
        Пример:
            manager = ExchangeManager()
            exchanges = manager.create_instances(['binance', 'okx'])
            # exchanges = [<ccxt.binance object>, <ccxt.okx object>]
        """

        if not user_exchanges:
            color.error(f"[ERROR] Вы не передали список используемых бирж")
            return []

        exchange_instances = []

        for user_exchange in user_exchanges:

            if user_exchange in self.exchanges_name:
                try :
                    exchange_class = getattr(ccxt, user_exchange)
                    exchange_instances.append(exchange_class({
                        'enableRateLimit': enable_rate_limit
                    }))
                    if show:
                        color.success(f"[SUCCESS] {user_exchange} Поддерживается")
                except Exception as ex:
                    color.error(f"[ERROR] Ошибка создания {user_exchange}: {ex}")

            else:
                color.error(f"[ERROR] {user_exchange} Не поддерживается")
        color.success(f'[SUCCESS] Создано {len(exchange_instances)} бирж')
        return exchange_instances

    def get_supported_instances(self,
                                show: bool = False,
                                limit: int = None,
                                enable_rate_limit: bool = True,
                                inplace: bool = False) -> list:
        """
        Создаёт и возвращает объекты всех поддерживаемых бирж.
        
        Args:
            show: Если True, выводит информацию в консоль
            limit: Максимальное количество создаваемых объектов бирж
            enable_rate_limit: Включить защиту от частых запросов
            inplace: Если True, сохраняет результат в self.exchanges_instances

        Returns:
            list: Список объектов бирж CCXT
        """
    
        # СОЗДАНИЕ ОБЪЕКТОВ БИРЖ
        exchanges_obj = []

        for exchange_name in self.exchanges_name:
            if limit is not None and len(exchanges_obj) >= limit: 
                break 
                
            try:
                exchange_class = getattr(ccxt, exchange_name)
                exchanges_obj.append(exchange_class({
                    'enableRateLimit': enable_rate_limit
                }))
            except Exception as ex:
                color.error(f'[ERROR] Не удалось создать объект {exchange_name}: {ex}')

        if inplace:
            self.exchanges_instances = exchanges_obj

            if show:  # Дополнительное сообщение
                color.info(f'[INFO] Сохранено в память: {len(exchanges_obj)} бирж')

        if show:
            exchanges_obj_count = len(exchanges_obj)
            color.success(f'[SUCCESS] Собрано {exchanges_obj_count} бирж')

        return exchanges_obj

    def get_supported_names(self,
                            show: bool = False,
                            limit: int = None,
                            inplace: bool = False) -> list:
        """
        Возвращает список названий всех поддерживаемых бирж.
        
        Args:
            show: Если True, выводит список в консоль
            limit: Максимальное количество бирж для возврата
        
        Returns:
            list: Список строк с названиями бирж
        """

        exchanges_name_list = ccxt.exchanges
        exchanges_name_list = sorted(exchanges_name_list)

        if show:
            exchange_name_count = len(exchanges_name_list)
            color.success(f'[SUCCESS] Собрано {exchange_name_count} бирж')

        if inplace:
            self.exchanges_name = exchanges_name_list

        if limit is not None and limit > 0:
            return exchanges_name_list[:limit]
        
        return exchanges_name_list

    def get_names_supported_ohlcv(self,
                                    show: bool = False,
                                    limit: int = None) -> list:
        """
        Возвращает список экземпляров бирж, поддерживающих OHLCV (свечные данные).
        
        Args:
            show (bool): Если True, выводит информационные сообщения о количестве бирж
            limit (int): Не используется в текущей реализации, оставлен для совместимости
        
        Returns:
            list: Список экземпляров бирж, поддерживающих fetchOHLCV
        """

        if not self.exchanges_name:
            color.error(f'[ERROR] Список бирж пуст, добавьте их через менеджер класса')
            return []
        
        instances = self.create_instances(self.exchanges_name)
        exchanges_supported_ohlcv = []
        exchanges_not_supported  = []

        for instance in instances:

            if instance.has.get('fetchOHLCV', False):
                exchanges_supported_ohlcv.append(instance)
            else:
                exchange_name = getattr(instance, 'name', 'Unknown')
                exchanges_not_supported.append(exchange_name)

        if show:
            total_count = len(instances)
            supported_count = len(exchanges_supported_ohlcv)
            not_supported_count = len(exchanges_not_supported)

            color.info(f'[INFO] OHLCV Поддерживает {supported_count} из {total_count} бирж')
            color.info(f'[INFO] OHLCV Не поддерживает {not_supported_count} бирж')

            if not_supported_count > 0:
                color.info(f'[INFO] Биржи без поддержки OHLCV: {", ".join(exchanges_not_supported)}')

        if limit is not None and limit > 0:
            return exchanges_supported_ohlcv[:limit]
        
        return exchanges_supported_ohlcv

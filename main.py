from exchange_manager import CryptoDataFetcher, ExchangeManager
from crypto_analyzer import CryptoAnalyzer
import pandas as pd
import ccxt

exchanges_list = ['binance', 'bybit', 'okx', 'kucoin']


exchange_manager = ExchangeManager()
fetcher = CryptoDataFetcher()
analyzer = CryptoAnalyzer()
# a = exchange_manager.get_supported_names(show=True, inplace=True)

exchanges_name_supported_ohlcv = exchange_manager.get_names_supported_ohlcv(show=True)
success_data, error_data = fetcher.fetch_ohlcv(
                                                symbols=['BTC/USDT', 'SOL/USDT'],
                                                exchanges=exchanges_name_supported_ohlcv,
                                                timeframe='1h',
                                                days_back=7,
                                                show=True
                                                )
# df = pd.DataFrame(success_data)
# analyzer.save_csv(path='./Data/CryptoData.csv', df=df)

# df_to_analyze = analyzer.load_csv(path='./Data/CryptoData.csv')
# ohlcv_data = analyzer.get_candles(df=df_to_analyze)
# grouped_data = ohlcv_data.groupby('exchange').agg(
#     max_high = pd.NamedAgg('high', aggfunc='max'),
#     min_low = pd.NamedAgg('low', aggfunc='min'),
#     mean_open = pd.NamedAgg('open', aggfunc='mean'),
#     mean_close = pd.NamedAgg('close', aggfunc='mean'),
#     max_date = pd.NamedAgg('timestamp', aggfunc=lambda x: ohlcv_data.loc[x.idxmax(), 'timestamp']),
#     min_date = pd.NamedAgg('timestamp', aggfunc=lambda x: ohlcv_data.loc[x.idxmin(), 'timestamp']),
# )
# analyzer.save_ohlcv_csv(path='./Data/CryptoDataCandles.csv', df=grouped_data, index=True)













# exchanges_list_obj = ExchangeManager().create_instances(exchanges_list)
# exchanges = CryptoDataFetcher(exchanges_list_obj)
# suc_data, err_data = exchanges.fetch_ohlcv(['BTC/USDT'], timeframe='1h', days_back=7)

# analazer = CryptoAnalyzer(exchanges=exchanges_list)
# analazer.save_json(data=suc_data, path='E:\Python\Project\Data', filename=f'Succes_OHLCV')
# analazer.save_ohlcv_csv(data=suc_data, path='E:\Python\Project\Data', filename=f'Succes_OHLCV')

# df_data = analazer.load_csv('E:\Python\Project\Data\Succes_OHLCV_2026-04-23_15-17-39.csv')
# analazer.to_lower(col='exchange')
# candles_data = analazer.get_candles()

# print(candles_data)

# result = candles_data.groupby('exchange').agg(
#     max_high = pd.NamedAgg(column='high', aggfunc='max'),
#     min_low = pd.NamedAgg(column='low', aggfunc='min'),
#     mean_close = pd.NamedAgg(column='close', aggfunc='mean'),
#     date_max = pd.NamedAgg(column='high', aggfunc=lambda x: candles_data.loc[x.idxmax(), 'timestamp']),
#     date_min = pd.NamedAgg(column='low', aggfunc=lambda x: candles_data.loc[x.idxmin(), 'timestamp']),
# )
# print(result.to_string())

# a = ccxt.bitget()
# print(a.has['fetchOHLCV'])
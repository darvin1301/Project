from exchange_manager import CryptoDataFetcher, ExchangeManager
from crypto_analyzer import CryptoAnalyzer
import pandas as pd

exchanges_list = ['binance', 'bybit', 'okx', 'kucoin']

exchanges_list_obj = ExchangeManager().create_instances(exchanges_list)
exchanges = CryptoDataFetcher(exchanges_list_obj)
suc_data, err_data = exchanges.fetch_ohlcv(['BTC/USDT'], timeframe='1h', days_back=7)

analazer = CryptoAnalyzer(exchanges=exchanges_list)
analazer.save_json(data=suc_data, path='E:\Python\Project\Data', filename=f'Succes_OHLCV')
analazer.save_ohlcv_csv(data=suc_data, path='E:\Python\Project\Data', filename=f'Succes_OHLCV')

df_data = analazer.load_csv('E:\Python\Project\Data\Succes_OHLCV_2026-04-23_15-17-39.csv')
analazer.to_lower(col='exchange')
candles_data = analazer.get_candles()

print(candles_data)

result = candles_data.groupby('exchange').agg(
    max_high = pd.NamedAgg(column='high', aggfunc='max'),
    min_low = pd.NamedAgg(column='low', aggfunc='min'),
    mean_close = pd.NamedAgg(column='close', aggfunc='mean'),
    date_max = pd.NamedAgg(column='high', aggfunc=lambda x: candles_data.loc[x.idxmax(), 'timestamp']),
    date_min = pd.NamedAgg(column='low', aggfunc=lambda x: candles_data.loc[x.idxmin(), 'timestamp']),
)
print(result.to_string())
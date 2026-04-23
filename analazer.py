import pandas as pd
import json
import csv
import os
from datetime import datetime, timedelta
from colors import color, ColorPrint, Colors


class DataProcessor:
    def __init__(self, exchanges: list[str]):
        self.exchanges = exchanges
        self.df = None
        self.result = {}
        self.path_csv = None
        self.path_json = None
    
    def _check_col_and_df(self, col: str, df: pd.DataFrame = None):

        if df is None:
            df = self.df
        
        if df is None or df.empty:
            color.error(f'[ERROR] Нет данных для обработки')
            return None, 'no_data'
        
        if not col:
            color.error('[ERROR] Вы не указали столбец')
            return None, 'no_column'
        
        if col not in df.columns:
            color.error(f'[ERROR] Столбец {col} не найден')
            return None, 'column_not_found'

        return df, None
        
    def _change_col_case(self, col: str, df: pd.DataFrame, case: str):
        df, error = self._check_col_and_df(col=col, df=df)
        if error:
            return df

        if case == 'upper':
            df[col] = df[col].str.upper()
        elif case == 'lower':
            df[col] = df[col].str.lower()
        elif case == 'capitalize':
            df[col] = df[col].str.capitalize()

        return df

    def load_from_csv(self, path: str):

        if not path:
            color.error('[ERROR] Вы не передали путь к файлу')
            return
        
        self.df = pd.read_csv(path)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        return self.df

    def save_dataframe_to_csv(self, path: str):

        if not path:
            color.error('[ERROR] Вы не передали путь куда сохранить файл')
            return
        
        if self.df is not None:
            self.df.to_csv(path, index=False)
            color.info(f'[INFO] Данные сохранены по пути {path}')
        else:
            color.error(f'[ERROR] Нет данных для сохранения')

    def save_to_json(self, data: list, path: str, filename: str = 'Crypto_Data') -> None:
        '''
        Сохранение данных в JSON файл.

        Args:
            data (list): Данные для сохранения (список словарей).
                Обычно возвращается методом get_price().
            path (str): Путь к директории для сохранения файла.
                Пример: 'data/', './results/', 'E:\\Питон\\Проект'
        '''
        if not data:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        full_filename = f"{filename}_{timestamp}.json"
        filepath = os.path.join(path, full_filename)
        self.path_json = filepath
        os.makedirs(path, exist_ok=True)

        try:

            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            color.info(f"[INFO] Данные успешно сохранены")
            color.info(f"[INFO] Путь к файлу: {filepath}")

        except Exception as ex:

            color.error(f"[ERROR] Произошла ошибка при сохранении данных в файл")
            color.error(ex)

    def save_ohlcv_to_csv(self, data: list, path: str, filename: str = 'Crypto_Data') -> None:
        '''
        Сохранение данных в CSV файл.

        Args:
            data (list): Данные для сохранения (список словарей).
                Каждый словарь - одна строка таблицы.
                Обычно возвращается методом get_ticker().
            path (str): Путь к директории для сохранения файла.
                Пример: 'data/', './results/', 'E:\\Питон\\Проект'
        '''
        if not data:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        full_filename = f"{filename}_{timestamp}.csv"
        filepath = os.path.join(path, full_filename)
        self.path_csv = filepath
        os.makedirs(path, exist_ok=True)

        try:

            with open(filepath, "w", newline="", encoding="utf-8") as file:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

        except Exception as ex:

            color.error(f"[ERROR] Произошла ошибка при сохранении данных в файл")
            color.error(ex)

    def change_col_data_to_upper(self, col: str,  df: pd.DataFrame = None):
        return self._change_col_case(col, df, 'upper')

    def change_col_data_to_lower(self, col: str, df: pd.DataFrame = None):
        return self._change_col_case(col, df, 'lower')
  
    def change_col_data_to_capitalize(self, col: str, df: pd.DataFrame = None):
        return self._change_col_case(col, df, 'capitalize')

    def group_data(self, col: str, agg: dict, data_frame: pd.DataFrame = None):

        df, error = self._check_col_and_df(col=col, df=data_frame)
        if error:
            return df if error in ['no_data', 'no_column', 'column_not_found'] else None

        if not agg:
            color.error(f'[ERROR] Словарь агрегации не может быть пустым')
            return df
        
        try:
            grouped_data = df.groupby(col).agg(agg)
            return grouped_data
        except Exception as ex:
            color.error(f'[ERROR] Произошла ошибка при группировке данных')
            color.error(f'[ERROR] Ошибка: {ex}')
            return df

    def get_candles(self, exchange_name: str = None, to_datetime: bool = True):
        all_candles = []

        for _, row in self.df.iterrows():

            if exchange_name != None and row['exchange'] != exchange_name:
                continue
            
            data = row['data']

            if isinstance(data, str):
                data = eval(data)

            for candle in data:
                candle[0] = pd.to_datetime(candle[0], unit='ms')
                all_candles.append({
                    'exchange': row['exchange'],
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5],
                })

        df_candles = pd.DataFrame(all_candles)


        return df_candles


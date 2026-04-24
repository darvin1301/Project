import pandas as pd
import json
import csv
import os
from datetime import datetime, timedelta
from colors import color, ColorPrint, Colors


class CryptoAnalyzer:
    """
    Анализирует OHLCV данные криптовалют с нескольких бирж.
    
    Этот класс загружает, обрабатывает и анализирует OHLCV данные.
    Предоставляет методы для группировки, агрегации и извлечения
    данных свечей для дальнейшего анализа.
    
    Пример:
        analyzer = CryptoAnalyzer(['binance', 'bybit', 'okx'])
        analyzer.load_csv('data.csv')
        candles = analyzer.get_candles()
        stats = analyzer.group_by('exchange', {'high': 'max', 'low': 'min'})
    """
    def __init__(self, exchanges: list[str] = None):
        self.exchanges = exchanges
        self.df = None
        self.result = {}
    
    def _validate_columns(self, col: str, df: pd.DataFrame = None):
        """
        Внутренний метод для валидации DataFrame и колонки.
        
        Проверяет:
        1. Существует ли DataFrame
        2. Не пустой ли он
        3. Указана ли колонка
        4. Существует ли указанная колонка
        
        Args:
            column: Название колонки для проверки
            dataframe: DataFrame для проверки (если None, использует self.data)
        
        Returns:
            tuple: (dataframe, error_type) или (dataframe, None) если всё хорошо
        """

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
        df, error = self._validate_columns(col=col, df=df)
        if error:
            return df

        if case == 'upper':
            df[col] = df[col].str.upper()
        elif case == 'lower':
            df[col] = df[col].str.lower()
        elif case == 'capitalize':
            df[col] = df[col].str.capitalize()

        return df

    def load_csv(self, path: str):
        """
        Загружает данные из CSV файла.
        
        Args:
            path: Путь к CSV файлу
        
        Returns:
            pd.DataFrame: Загруженный DataFrame или None при ошибке
        """

        if not path:
            color.error('[ERROR] Вы не передали путь к файлу')
            return
        
        self.df = pd.read_csv(path)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        return self.df

    def save_csv(self,
                path: str = None, 
                df: pd.DataFrame = None, 
                index: bool = False, 
                encoding: str = 'utf-8') -> str:
        """
        Сохраняет DataFrame в CSV файл.
        
        Args:
            path: Путь для сохранения файла
        """

        if not path:
            color.error('[ERROR] Вы не передали путь куда сохранить файл')
            return None
        
        data_to_save = df if df is not None else self.df
        
        if data_to_save is None:
            color.error('[ERROR] Нет данных для сохранения')
            return None
        
        try:
            data_to_save.to_csv(path, index=index, encoding=encoding)
            color.success(f'[SUCCESS] Данные сохранены: {path}')
            return path
        except Exception as ex:
            color.error(f'[ERROR] Ошибка сохранения: {ex}')
            return None

    def save_json(self, data: list, path: str, filename: str = 'Crypto_Data') -> str:
        """
        Сохраняет данные в JSON файл.
        
        Args:
            data: Список словарей для сохранения
            path: Путь к директории для сохранения
            filename: Базовое имя файла (к нему добавится timestamp)
        """
        if not path:
            color.error('[ERROR] Вы не передали путь для сохранения')
            return None
        
        if not data:
            color.error('[ERROR] Нет данных для сохранения')
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        full_filename = f"{filename}_{timestamp}.json"
        filepath = os.path.join(path, full_filename)
        os.makedirs(path, exist_ok=True)

        try:

            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            color.info(f"[INFO] Данные успешно сохранены")
            color.info(f"[INFO] Путь к файлу: {filepath}")
            return filepath

        except Exception as ex:

            color.error(f"[ERROR] Произошла ошибка при сохранении JSON")
            color.error(ex)
            return None

    def save_ohlcv_csv(self,
                        path: str,
                        df: pd.DataFrame = None,
                        index: bool = False, 
                        encoding: str = 'utf-8') -> str:
        """
        Сохраняет OHLCV данные в CSV файл.
        
        Args:
            data: Список словарей с OHLCV данными
            path: Путь к директории для сохранения
            filename: Базовое имя файла (к нему добавится timestamp)
        """


        if not path:
            color.error('[ERROR] Вы не передали путь куда сохранить файл')
            return None
    
        
        if df is None:
            color.error('[ERROR] Нет данных для сохранения')
            return None
        
        try:
            df.to_csv(path, index=index, encoding=encoding)
            color.success(f'[SUCCESS] Данные сохранены: {path}')
            return path
        
        except Exception as ex:
            color.error(f'[ERROR] Ошибка сохранения: {ex}')
            return None






























        if not data:
            return None

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
                return filepath
            
        except Exception as ex:

            color.error(f"[ERROR] Произошла ошибка при сохранении данных в файл")
            color.error(ex)

    def to_upper(self, col: str,  df: pd.DataFrame = None):
        """
        Преобразует текст в указанной колонке в ВЕРХНИЙ регистр.
        
        Args:
            column: Название колонки
            dataframe: DataFrame для обработки (если None, использует self.data)
        
        Returns:
            pd.DataFrame: DataFrame с преобразованной колонкой
        """

        return self._change_col_case(col, df, 'upper')

    def to_lower(self, col: str, df: pd.DataFrame = None):
        """
        Преобразует текст в указанной колонке в нижний регистр.
        
        Args:
            column: Название колонки
            dataframe: DataFrame для обработки (если None, использует self.data)
        
        Returns:
            pd.DataFrame: DataFrame с преобразованной колонкой
        """
                
        return self._change_col_case(col, df, 'lower')
  
    def to_capitalize(self, col: str, df: pd.DataFrame = None):
        """
        Преобразует текст в указанной колонке: первая буква заглавная, остальные маленькие.
        
        Args:
            column: Название колонки
            dataframe: DataFrame для обработки (если None, использует self.data)
        
        Returns:
            pd.DataFrame: DataFrame с преобразованной колонкой
        """
                
        return self._change_col_case(col, df, 'capitalize')

    def group_by(self, col: str, agg: dict, data_frame: pd.DataFrame = None):
        """
        Группирует данные по указанной колонке с применением агрегации.
        
        Args:
            column: Название колонки для группировки
            aggregation: Словарь агрегации, например:
                {'high': 'max', 'low': 'min', 'close': 'mean', 'volume': 'sum'}
            dataframe: DataFrame для обработки (если None, использует self.df)
        
        Returns:
            pd.DataFrame: Сгруппированные и агрегированные данные
        
        Пример:
            result = analyzer.group_by('exchange', {
                'high': 'max',
                'low': 'min',
                'close': 'mean'
            })
        """

        df, error = self._validate_columns(col=col, df=data_frame)
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

    def get_candles(self, exchange_name: str = None, df: pd.DataFrame = None, show: bool = False) -> pd.DataFrame:
        """
        Извлекает все свечи из загруженных данных и возвращает в виде DataFrame.
        
        Этот метод "разворачивает" вложенные списки свечей в плоскую таблицу,
        где каждая строка - одна свеча.
        
        Args:
            exchange_name: Название биржи для фильтрации (если None - все биржи)
            as_datetime: Если True, преобразует timestamp в datetime
        
        Returns:
            pd.DataFrame: DataFrame со свечами (колонки: exchange, timestamp, open, high, low, close, volume)
        
        Пример:
            Получить все свечи
            all_candles = analyzer.get_candles()
            
            Получить свечи только Binance
            binance_candles = analyzer.get_candles(exchange_name='binance')
        """
        data_df = df if df is not None else self.df

        if data_df is None:
            color.error('[ERROR] Нет данных для обработки (переданный df и self.df пусты)')
            return pd.DataFrame()
        
        if data_df.empty:
            color.warning('[WARNING] DataFrame пуст')
            return pd.DataFrame()
        
        all_candles = []

        for _, row in data_df.iterrows():

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
        if show:
            color.info(f'[INFO] Собрано {len(all_candles)} свечей')

        return df_candles


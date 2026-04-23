# colors.py
"""
Модуль с цветами для терминала
Можно использовать в любом классе/файле
"""

class Colors:
    """ANSI color codes for terminal output"""
    # Текст
    RED = '\033[91m'
    GREEN = '\033[92m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Стили
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Фоны
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    
    RESET = '\033[0m'


class ColorPrint:
    """Класс-помощник для цветного вывода"""
    
    @staticmethod
    def success(text, end='\n'):
        print(f"{Colors.GREEN} {text}{Colors.RESET}", end=end)
    
    @staticmethod
    def error(text, end='\n'):
        print(f"{Colors.RED} {text}{Colors.RESET}", end=end)
    
    @staticmethod
    def warning(text, end='\n'):
        print(f"{Colors.YELLOW} {text}{Colors.RESET}", end=end)
    
    @staticmethod
    def info(text, end='\n'):
        print(f"{Colors.CYAN} {text}{Colors.RESET}", end=end)
    
    @staticmethod
    def header(text, end='\n'):
        print(f"{Colors.BOLD}{Colors.MAGENTA}{text}{Colors.RESET}", end=end)
    
    @staticmethod
    def line(char='=', length=50):
        print(f"{Colors.GRAY}{char * length}{Colors.RESET}")


# Для удобства создаем экземпляр
color = ColorPrint()
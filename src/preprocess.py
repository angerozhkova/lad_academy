import re
import emoji

def preprocess_text(text: str) -> str:
    """Предобрабатывает текст для анализа моделью.

    Выполняет очистку текста: удаляет URL, код, HTML-теги, эмодзи, лишние символы,
    сохраняет строки с русским текстом, приводит к нижнему регистру.

    Args:
        text (str): Входной текст для обработки.

    Returns:
        str: Предобработанный текст. Возвращает пустую строку, если текст пустой
             или содержит только пунктуацию.
    """
    # Проверка типа входного текста
    if not isinstance(text, str):
        return ""

    # Компиляция паттерна для удаления URL
    url_pattern = re.compile(r"https?://\S+|www\.\S+")

    # Определение паттернов для удаления кода
    code_patterns = [
        r'```[\s\S]*?```',  # Блоки кода в тройных кавычках
        r'<[^>]+>[\s\S]*?</[^>]+>',  # HTML-теги
        r'\b(def|function|class|import|from|if|else|elif|for|while|return|try|except|async|await)\b[^{а-яА-Я]*[;\n]',  # Ключевые слова
        r'(?<!\w)[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^{а-яА-Я]+?(?=[\s\n]|$)',  # Присваивания
        r'(?<!\w)[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\([^{а-яА-Я]*\)',  # Вызовы методов
        r'(?<!\w)[A-Za-z_][A-Za-z0-9_]*\([^{а-яА-Я]*\)',  # Функции
        r'(?<!\w)[A-Z]+\b(?:\.[A-Z]+)*\([^{а-яА-Я]*\)'  # Константы
    ]

    # Временная замена скобок с русским текстом
    placeholder = "§§§§§"
    brackets_with_russian = re.compile(r'([(\[{])(?=[^])}]*[а-яА-Я])(.*?)([)\]}])')
    preserved = []

    def save_brackets(match):
        """Сохраняет скобки с русским текстом, заменяя их на placeholder."""
        preserved.append(match.group(0))
        return placeholder

    # Замена скобок с русским текстом на placeholder
    text = brackets_with_russian.sub(save_brackets, text)

    # Удаление кода по каждому паттерну
    for pattern in code_patterns:
        text = re.sub(pattern, "", text, flags=re.MULTILINE)

    # Удаление скобочных конструкций БЕЗ русских букв
    text = re.sub(r'\([^()]*[а-яА-Я][^()]*\)', '', text)  # сохраняем скобки с русским текстом
    text = re.sub(r'\([^()]*\)', '', text)  # удаляем оставшиеся скобки
    text = re.sub(r'\{[^{}]*\}', '', text)
    text = re.sub(r'\[[^\[\]]*\]', '', text)

    # Восстановление сохраненных скобок с русским текстом
    for item in preserved:
        text = text.replace(placeholder, item, 1)

    # Удаление строк без русских букв
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if re.search('[а-яА-Я]', line):
            processed_lines.append(line)
        elif not line.strip():
            processed_lines.append('')
            
    text = "\n".join(processed_lines)

    # Замена переносов строк, табуляций и множественных пробелов
    text = re.sub(r"[\n\r\t]", " ", text)
    # Удаление специальных символов
    text = re.sub(r"[•▪★✔►–—«»…]", "", text)
    # Нормализация повторяющихся знаков препинания
    text = re.sub(r"([!?])\1+", r"\1", text)
    # Замена неразрывных пробелов и нулевых пробелов
    text = text.replace(u"\xa0", " ").replace(u"\u200b", "")
    # Удаление эмодзи
    text = emoji.replace_emoji(text, replace="")
    # Удаление лишних пробелов и обрезка
    text = re.sub(r"\s+", " ", text).strip()
    # Удаление URL
    text = url_pattern.sub('', text)
    # Приведение к нижнему регистру
    text = text.lower()

    # Проверка на пустой текст или текст только из пунктуации
    if not text or re.match(r"^[.!?,;:]+$", text):
        return ""
    return text

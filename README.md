# Классификатор сообщений
Этот модуль предоставляет обученную модель RuModernBert-base и функцию предобработки для бинарной классификации текстов.

## Предоставленные файлы
- `src/preprocess.py`: Функция предобработки текста (`preprocess`), удаляет URL, код, HTML-теги, эмодзи, нормализует текст.
- `src/config.py`: Конфигурация путей (например, к модели) и параметров (максимальная длина).
- `model/threshold.txt`: Файл с порогом классификации (значение для разделения классов, например, 0.5). Модель и токенизатор доступны в релизе [v3.0](https://github.com/lad-academy/search-candidates-bot/releases/tag/v3.0).
- `training/train_rumodernbert.ipynb`: Jupyter Notebook с кодом для дообучения модели.
- `training/hard_negative_dataset.csv`: Датасет с нецелевыми сообщениями с меткой 0 (формат: текст, метка).
- `training/real_label_1_dataset.csv`: Датасет с целевыми сообщениями с меткой 1 (формат: текст, метка).
- `training/syn_label_1_dataset.csv`: Датасет со сгенерированными сообщениями с меткой 1.
- `training/test.csv`: Датасет для тестирования без меток.
- `requirements.txt`: Зависимости для выполнения кода.


## Использование
Для использования модели в парсере:
1. **Установите зависимости с фиксированными версиями:**
```python
pip install torch==2.6.0+cu124 -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers==4.52.4
pip install emoji==2.14.0
pip install numpy==1.26.4
```
---  
2.  **Загрузите модель и токенизатор из релиза:**
    - Перейдите по ссылке [v3.0](https://github.com/lad-academy/search-candidates-bot/releases/tag/v3.0).
    - Скачайте файлы и распакуйте в message_classifier/model/.
---
3. **Импортируйте необходимые модули, конфигурацию и предобработку:**
```python
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from message_classifier.src.config import MODEL_PATH, MAX_LENGTH
from message_classifier.src.preprocess import preprocess
```
---
4. **Загрузите порог:**
```python
with open(f"{MODEL_PATH}/threshold.txt", "r") as f:
    threshold = float(f.read())
```
<p>Порог используется для принятия решения в бинарной классификации: если вероятность предсказания выше порога, сообщение относится к классу 1, иначе — к классу 0.</p>

---
5. **Обработайте сообщение и загрузите модель:**
```python
text = "привет!\nЭто тест"
processed_text = preprocess(text)
print(processed_text)  # Ожидается: "привет! тест"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
```
---
6. **Выполните токенизацию сообщения:**
```python
tokens = tokenizer(processed_text,
                   max_length=MAX_LENGTH,
                   padding=True,
                   truncation=True,
                   return_tensors="pt")
print(tokens)  # Ожидается: объект с input_ids, attention_mask и т.д.
```
---
7. **Выполните предсказание.**
```python
# Переключение модели в режим оценки
model.eval()

# Выполнение инференса без градиентов
with torch.no_grad():
    outputs = model(**{k: v.to("cuda") for k, v in tokens.items()})

# Вычисление вероятности
probs = torch.sigmoid(outputs.logits.squeeze()).cpu().numpy()

# Получение предсказания
pred = (probs >= threshold).astype(int)

# Вывод результата
print(f"Текст: {text}")
print(f"Класс: {pred} (вероятность: {probs:.3f})")
```


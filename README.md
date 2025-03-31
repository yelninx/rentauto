# rentauto
## Программа для аренды авто с выдуманными ценами и отсутсвием безопасности
Код на питоне 3.13, библиотеки - PyQt6 для GUI и sqlite3 для работы с БД.
Сборка через pyinstaller

## Сборка
```Python
pip isntall pyinstaller
pyinstaller --onefile --windowed main.py
```
В папке с exe файлом нужно положить базу данных cars.sqlite, а так же папку resources в которой есть как минимум файл stock.jpg для изображения по умолчанию
:)

### Структура cars.sqlite
#### Таблица cars
```
id INTEGER
name TEXT
brand TEXT
year INTEGER
cost INTEGER
info TEXT
image_path TEXT
is_rented INTEGER
```
#### Таблица users
```
id INTEGER
login TEXT
password TEXT
isadmin BOOLEAN
```

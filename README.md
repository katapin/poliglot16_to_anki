# Poliglot16 to anki
Convert word collections from [poliglot16.ru](https://poliglot16.ru) to [Anki](https://apps.ankiweb.net) decks.

Конвертация пользовательских наборов слов с сайта [poliglot16.ru](https://poliglot16.ru) в колоды карточек [Anki](https://ru.wikipedia.org/wiki/Anki). Результат может быть сохранен как в виде простого CSV-файла (`poliglot2csv.py`), так и в виде anki-пакета `*.apkg` (`poliglot2anki.py`). В anki-пакет также будут добавлены звуковые файлы с произношениями слов с сайта, которые будут автоматически проигрываться при показе слова. 

### Зависимости
Для работы необходима библиотека `requests-HTML`. Для создания `*.apkg` файлов также потребуется питоновский пакет `anki` (официальная библиотека от авторов программы).

### Примеры
Для авторизации на сайте требуется пара логин-пароль пользователя, либо токен. Также аргументами являются имя файлы для сохранения результата и название набора слов на сайте (либо его ID). За один раз можно указать несколько наборов, но все они будут объединены в одну колоду. Для версии `poliglot2anki.py` можно указать пользовательское название колоды ключом `--deckname`.
```
python poliglot2csv.py --login [e-mail] --password [password] --outfile words.csv basic food 12345
python poliglot2csv.py --token [userid]:[SESSIONID] --outfile words.csv basic food 12345
python poliglot2anki.py --token [userid]:[SESSIONID] --deckname MyDeck --outfile words.apkg basic 12345
python poliglot2anki.py --token [userid]:[SESSIONID] --deckname Food --outfile food.apkg food
```
См. также справку, вывод команды `--help`.

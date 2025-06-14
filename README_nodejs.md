# Скачивание файлов по артикулам из Excel (Node.js)

Этот скрипт написан на Node.js и читает Excel-файл, берёт артикулы из колонки C (начиная с 5-й строки) и URL-ы картинок из колонки H (разделённые `;`). Для каждого артикула создаётся папка, и все картинки скачиваются в неё параллельно. В консоль выводится прогресс, а все неудачные загрузки сохраняются в `failed_downloads.txt`.

---

## 1. Проверка окружения

Перед запуском необходимо убедиться, что на компьютере установлен Node.js (версия ≥ 14).

1. Открой терминал (или Командную строку в Windows).
2. Введи команду:
   ```bash
   node --version
   ```
   - Если увидишь что-то вроде `v16.20.0`, значит Node.js установлен.
   - Если выдаёт ошибку («команда не найдена» или похожее), то Node.js не установлен или не добавлен в PATH.

---

## 2. Установка зависимостей

Все зависимости уже указаны в `package.json`. Чтобы установить их, выполни в папке со скриптом:

```bash
npm install
```

Это создаст папку `node_modules` и загрузит нужные библиотеки (например, `xlsx` и `axios`).

---

## 3. Подготовка скрипта

Убедись, что в текущей папке лежит файл:

- `download_from_excel.js` — скрипт для скачивания (Node.js).

Также должен быть рядом твой Excel-файл с данными.

---

## 4. Подготовка Excel-файла

1. Проверь, что твой Excel-файл:
   - Колонка C (артикулы) заполнена начиная с 5-й строки.
   - Колонка H (URL-ы) в тех же строках содержит строки формата:
     ```
     https://…/1.webp;https://…/2.webp;https://…/3.webp
     ```
   - Файл сохранён в формате `.xlsx`.

2. Помести его в удобное место и запомни путь к нему.

---

## 5. Запуск скрипта

В папке со скриптом выполни команду:

```bash
node download_from_excel.js путь/к/вашему_файлу.xlsx
```

### Примеры

- Если Excel-файл `products.xlsx` находится в той же папке:
  ```bash
  node download_from_excel.js products.xlsx
  ```

После запуска:

- Для каждого артикула создаётся папка с его названием.
- Все URL-ы из колонки H разбиваются по `;` и скачиваются в соответствующую папку.
- В консоль выводятся сообщения:
  ```
  [OK]  https://…/1.webp → ART123/1.webp
  [ERR] https://…/2.webp  (TimeoutError или другая ошибка)
  ```
- Все неудачные URL-ы сохраняются в файл `failed_downloads.txt` в той же папке, где скрипт.

---

## 6. Параметры (по желанию)

По умолчанию все загрузки идут параллельно (Promise.all). Если нужно контролировать число одновременных запросов, можно доработать скрипт, например, через библиотеку `p-limit`.

---

## 7. Советы

- Проверь стабильность интернета — при перебоях часть файлов может не загрузиться.
- Если много URL-ов и появляются ошибки таймаута, можно разбить задачу на несколько запусков или добавить задержку между запросами.
- После первого запуска проверь `failed_downloads.txt` и при необходимости запусти скрипт заново только для тех URL-ов.

---

Теперь всё готово. Удачного скачивания!

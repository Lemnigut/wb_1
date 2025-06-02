import os
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

def download_file(article, url, failed_list, lock):
    """
    Скачивает один файл по url в папку article.
    В случае ошибки добавляет url в failed_list.
    """
    try:
        response = requests.get(url, timeout=15, stream=True)
        response.raise_for_status()
        filename = url.rstrip('/').split('/')[-1]
        dest_path = os.path.join(article, filename)

        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK]  {url} → {article}/{filename}")
    except Exception as e:
        print(f"[ERR] {url}  ({e})")
        with lock:
            failed_list.append(url)

def main():
    parser = argparse.ArgumentParser(
        description="Скачивает файлы из Excel (колонка C – артикулы, H – URL через ;) в папки по артикулам"
    )
    parser.add_argument("excel_file", help="Путь к Excel-файлу")
    parser.add_argument("--workers", type=int, default=8, help="Число потоков для скачивания (по умолчанию 8)")
    args = parser.parse_args()

    # Читаем лист без заголовков, чтобы точные индексы совпадали (C→2, H→7)
    df = pd.read_excel(args.excel_file, header=None)

    tasks = []
    for idx, row in df.iterrows():
        if idx < 4:
            continue  # пропускаем первые 4 строки (начинаем с 5-й)
        article = row[2]  # колонка C (индекс 2)
        urls_cell = row[7]  # колонка H (индекс 7)

        if pd.isna(article) or pd.isna(urls_cell):
            continue

        art = str(article).strip()
        urls = [u.strip() for u in str(urls_cell).split(";") if u.strip()]
        if not art or not urls:
            continue

        # создаём папку артикула (если ещё нет)
        os.makedirs(art, exist_ok=True)

        for url in urls:
            tasks.append((art, url))

    if not tasks:
        print("Нет задач для скачивания.")
        return

    failed = []
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        for art, url in tasks:
            futures.append(executor.submit(download_file, art, url, failed, lock))
        for fut in as_completed(futures):
            pass  # все логи внутри download_file

    # Записываем неудачные URL-ы в файл
    if failed:
        try:
            with open("failed_downloads.txt", "w", encoding="utf-8") as fout:
                for u in failed:
                    fout.write(u + "\n")
            print(f"\n[INFO] Список неудачных загрузок сохранён в failed_downloads.txt ({len(failed)} шт.)")
        except Exception as e:
            print(f"[ERR] Не удалось записать failed_downloads.txt: {e}")
    else:
        print("\n[INFO] Все файлы успешно скачаны.")

if __name__ == "__main__":
    main()

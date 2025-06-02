// download_from_excel.js

const fs = require('fs');
const path = require('path');
const XLSX = require('xlsx');
const axios = require('axios');

if (process.argv.length < 3) {
    console.error('Использование: node download_from_excel.js <путь_к_excel>');
    process.exit(1);
}

const excelPath = process.argv[2];
let failedUrls = [];

async function downloadFile(article, url) {
    const filename = url.split('/').pop().split('?')[0];
    const destPath = path.join(article, filename);

    try {
        const response = await axios.get(url, { responseType: 'stream', timeout: 15000 });
        await new Promise((resolve, reject) => {
            const writer = fs.createWriteStream(destPath);
            response.data.pipe(writer);
            writer.on('finish', resolve);
            writer.on('error', reject);
        });
        console.log(`[OK]  ${url} → ${path.join(article, filename)}`);
    } catch (err) {
        console.log(`[ERR] ${url}  (${err.message})`);
        failedUrls.push(url);
    }
}

async function main() {
    // читаем книгу и берём первый лист
    const workbook = XLSX.readFile(excelPath);
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 });

    // собираем все задачи
    const tasks = [];
    for (let i = 4; i < rows.length; i++) {
        const row = rows[i];
        const article = row[2];
        const urlsCell = row[7];
        if (!article || !urlsCell) continue;

        const art = String(article).trim();
        const urlsList = String(urlsCell)
            .split(';')
            .map(u => u.trim())
            .filter(u => u.length);

        if (!art || urlsList.length === 0) continue;

        // создаём папку артикула, если нет
        if (!fs.existsSync(art)) {
            try {
                fs.mkdirSync(art, { recursive: true });
            } catch (e) {
                console.error(`[ERR] Не удалось создать папку "${art}": ${e.message}`);
                continue;
            }
        }

        // формируем задачи
        for (const url of urlsList) {
            tasks.push({ article: art, url });
        }
    }

    if (tasks.length === 0) {
        console.log('Нет задач для скачивания.');
        return;
    }

    // параллельный запуск всех загрузок
    await Promise.all(tasks.map(t => downloadFile(t.article, t.url)));

    // запись списка неудачных загрузок
    if (failedUrls.length) {
        try {
            fs.writeFileSync('failed_downloads.txt', failedUrls.join('\n'), 'utf-8');
            console.log(`\n[INFO] Список неудачных загрузок сохранён в failed_downloads.txt (${failedUrls.length} шт.)`);
        } catch (e) {
            console.error(`[ERR] Не удалось записать failed_downloads.txt: ${e.message}`);
        }
    } else {
        console.log('\n[INFO] Все файлы успешно скачаны.');
    }
}

main();

# Инструкция

Установка зависимостей:

```bash
pip install -r requirements.txt
```

### Запуск команды

```bash
python parser.py  --directoryIn=directoryIn --directoryOut=directoryOut --fileIn="/Users/meryzhanybekova/Desktop/Work Project/parsing_files/constant/pdf/1109-12-ОВ1.pdf" --fileOut=test.xml
```

### Аргументы
> Список: <br>
> * directoryIn
> * directoryOut
> * fileIn
> * projectId
> * objectId
> * fileId
> * fileOut

### Пример заполнения аргумента
```bash
--directoryIn="/var/www/www-root/data/www/costana.testdom.ru/costana/public/storage/projects/4/Тестовый проект####1662128525####6312118d30074"
--directoryOut="/var/www/www-root/data/www/costana.testdom.ru/costana/storage/app/public/projects/4/specification/Тестовый проект"
--fileIn="/var/www/www-root/data/www/costana.testdom.ru/costana/public/storage/projects/4/Тестовый проект####1662128525####6312118d30074/266AR-16-(266AR-СПД2-16)-ЧС####1662128525####6312118d2f534.pdf" 
--projectId="Тестовый проект"
--objectId="4" 
--fileId="6312118d2f534" 
--fileOut="/var/www/www-root/data/www/costana.testdom.ru/costana/storage/app/public/projects/4/specification/Тестовый проект/6312118d2f534.xml"
```

```bash
python main.py  --directoryIn="/Users/meryzhanybekova/Desktop/Work Project/parsing_files/directoryIn" --directoryOut="/Users/meryzhanybekova/Desktop/Work Project/parsing_files/directoryOut" --fileOut="/Users/meryzhanybekova/Desktop/Work Project/parsing_files/directoryOut/test.xml" --fileIn="/Users/meryzhanybekova/Desktop/Work Project/parsing_files/constant/pdf/1109-27-ОВ1.pdf"
```

## License

[Telegram](https://t.me/baha996)
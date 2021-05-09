# weatherAggregator
API + cli для сбора и выдачи данных о погоде в выбранных городах на Flask.

## CLI
```flask init-db``` - инициализация базы данных. При этом в БД добавляются источники из weatherAggregator/weather_sources.sql.

```flask set-keys SOURCE_1 KEY_1 [SOURCE_2 KEY_2 ...]``` - сохранение ключей API для последующего использования.

```flask add-city CITY COUNTRY_CODE``` - добавление города в БД. Команда стягивает координаты и id города из источников погоды.

```flask fetch``` - получение данных о текущей погодe во всех городах из всех источников.

## API
/weather - все собранные данные о погоде.

Опциональные параметры:
- city - город, для которого вернуть данные;
- country - двухбуквенный код страны, для которой вернуть данные;
- source - название источника погоды, для которого вернуть данные.

Пример:
http://127.0.0.1:5000/weather?city=Moscow&source=openweathermap.org&country=RU
```
{
  data: [
    {
      city: "Moscow",
      country: "RU",
      datetime: "Sun, 09 May 2021 20:32:13 GMT",
      ob_dt: 1620581533,
      source: "openweathermap.org",
      temp: 8.96
    }
  ]
}
```
ob_dt - время получения данных источником в секундах. datetime - тоже самое время, но в читаемом виде.

## Установка и запуск
1. Клонируйте проект и перейдите в его основную директорию
2. Создайте виртуальное окружение: ```python -m venv venv```
3. Активируйте виртуальное окружение: ```source venv/bin/activate```
4. Установите приложение: ```pip install -e .```
5. Установите переменную окружения приложения: ```export FLASK_APP=weatherAggregator```

Теперь сервер можно запустить с предустановленной базой данных: ```flask run```
Посмотреть содержимое можно в службе /weather: http://127.0.0.1:5000/weather

## Работа с БД и источниками погоды
Сначала нужно задать ключи API источников: ```flask set-keys openweathermap.org key_1 weatherbit.io key_2```
Инициализация бд (создание новой вместо стартовой или текущей): ```flask init-db```
Добавление города: ```flask add-city Moscow RU```
Получение данных о погоде из источников: ```flask fetch```

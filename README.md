# weatherAggregator
API + cli для сбора и выдачи данных о погоде в выбранных городах на Flask.

## CLI
```flask init-db``` - инициализация базы данных. При этом в БД добавляются источники из weatherAggregator/weather_sources.sql.

```flask set-keys SOURCE_1 KEY_1 [SOURCE_2 KEY_2 ...]``` - сохранение ключей API для последующего использования.

```flask add-city CITY COUNTRY_CODE``` - добавление города в БД. Команда стягивает координаты и id города из источников погоды.

```flask fetch``` - получение данных о текущей погоды во всех городах из всех источников.

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

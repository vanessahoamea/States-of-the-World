# States-of-the-World
This projects consists of two main components:
- `crawler.py` - a script that scrapes Wikipedia pages of various countries and stores information about each country in a database, such as: its name, capital, spoken languages, population, etc.
- `client.py` - used for making API calls to obtain information about countries stored in the database.

## API Documentation
To be able to make calls to the API, run the `api.py` file and access `http://localhost:5000`.

### GET `/all`
Returns a list of all the countries in the database. To get only the countries to which a specific condition applies, set the necessary query parameters (`name`, `capital`, `language`, `population`, `density`, `area`, `time_zone`, `currency`, `government`).

Example:
```
GET http://localhost:5000/all?language=english&time_zone=utc+2
[
  {
    "name": "Botswana",
    "capital": "Gaborone",
    "language": "[English]",
    "population": 2384246,
    "density (per km2)": 4.1,
    "area (km2)": 581730.0,
    "time_zone": "UTC+2",
    "currency": "BWP",
    "government": "Unitary dominant-party parliamentary republic with an executive presidency"
  },
  ...
]
```

### GET `/top-10/<parameter>`
Returns a list of 10 countries with the highest `population`, `density`, or `area`. If no value for `<parameter>` is given, it will default to `population`.

Example:
```
GET http://localhost:5000/top-10/area
[
  {
    "name": "Russia",
    "capital": "Moscow",
    "language": "[Russian]",
    "population": 147182123,
    "density (per km2)": 8.4,
    "area (km2)": 17098246.0,
    "time_zone": "UTC+2",
    "currency": "RUB",
    "government": "Federal semi-presidential republic under an authoritarian dictatorship"
  },
  ...
]
```

/*
* API general
*/
var req_week = {
  "type": "week",
  "start": "2017-01-01", // domingo
  "crime_type": "all",
  "number_of_officers": 4500
}

var req_month = {
  "type": "month",
  "start": "2018-01",
  "crime_type": "all",
  "number_of_officers": 4500
}

// Opcion 1
var res = {
  "crimes": { // suma de todos los tipos de crimenes (por ejemplo, "all") en una semana/mes
    "03837": 1284,
    "04472": 124
  },
  "officers": { // oficiales asignados a un zipcode
    "03837": 12,
    "04472": 1
  }
}

// Opcion 2
var res = [
  {
    "zipcode": "03837",
    "crimes": 1283,
    "officers": 12
  },
  {
    "zipcode": "28913",
    "crimes": 1283,
    "officers": 12
  }
]

/*
* API pintar time-series
*/
var req_time_series = {
  "start": "2017-01-01", // domingo
  "end": "2017-01-07", // sábado
  "zipcode": "03837"
}

var res_time_series = { // Prediccion por dia
  "2021-12-05": 138,
  "2021-12-06": 138,
  "2021-12-07": 138,
  "2021-12-08": 138,
  "2021-12-09": 138,
  "2021-12-10": 138
}
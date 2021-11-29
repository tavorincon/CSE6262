# CSE6242 Project

## For running the webserver locally
Run `make server`

## Displaying maps
The project uses MapBox for obtaining the map tiles. You need to generate an [Access Token](https://account.mapbox.com/access-tokens/), then copy and paste it in the `.env` file.

### Obtaining geoJSON boundaries
For displaying the ZIP Codes polygons we obtained the boundaries from a freemium API in RapidAPI. If you want to refresh the data you need to create an API key [here](https://rapidapi.com/VanitySoft/api/boundaries-io-1/), then copy and paste it in the `.env` file.
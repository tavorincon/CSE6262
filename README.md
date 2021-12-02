# CSE6242 Project

# First steps
1) Clone this repository in your PC
2) Copy the `KCPD_Crime_Data_Complete.csv` file into `data/crime`
3) Rename `.env-example` to `.env`. This file contains your environment configuration. The `.env` should not be commited to GitHub, since each developer / server using the application could require a different environment configuration. Furthermore, this would be a security risk, since any sensitive credentials would get exposed.
4) For running the webserver locally run `make server`

## Displaying maps
The project uses MapBox for obtaining the map tiles. You need to generate an [Access Token](https://account.mapbox.com/access-tokens/), then copy and paste it in the `.env` file.

### Obtaining geoJSON boundaries
For displaying the ZIP Codes polygons we obtained the boundaries from a freemium API in RapidAPI. If you want to refresh the data you need to create an API key [here](https://rapidapi.com/VanitySoft/api/boundaries-io-1/), then copy and paste it in the `.env` file.

## Credits
- Ismael Montes
- Gustavo Rincon
- Mauricio J Diaz
- Juan C Pineda
- Martin Rodriguez
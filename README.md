# CSE6242 Project

# First steps
1) Clone this repository in your PC. For first timers, follow [these](https://www.jcchouinard.com/clone-github-repository-on-windows/) instructions.
2) Copy the `KCPD_Crime_Data_Complete.csv` file available [here](https://b.gatech.edu/3EsQa1M) into `data/crime`
3) Copy the `init.sql` file available [here](https://b.gatech.edu/3EsQa1M) into `db/`
4) Rename `.env-example` to `.env`. This file contains your environment configuration. The `.env` should not be commited to GitHub, since each developer / server using the application could require a different environment configuration. Furthermore, this would be a security risk, since any sensitive credentials would get exposed. Then, follow the "Obtain credentials tokens for .env file" instructions below to populate the .env file

# Obtain credentials tokens for .env file
## Displaying maps
The project uses MapBox for obtaining the map tiles. You need to generate an [Access Token](https://account.mapbox.com/access-tokens/), then copy and paste it in the `.env` file. (You must sign-up for an account)

### Obtaining geoJSON boundaries
For displaying the ZIP Codes polygons we obtained the boundaries from a freemium API in RapidAPI. If you want to refresh the data you need to create an API key [here](https://rapidapi.com/VanitySoft/api/boundaries-io-1/), then copy and paste it in the `.env` file. (Make sure to Sign-up and Subscribe before copying access token)


# Deploying application

## Via Docker (RECOMMENDED METHOD)
1) Open a terminal (i.e. Git BASH in Windows) inside the root of the cloned repository and run `docker-compose up --build`
2) Once the containers has been started you may go to http://localhost:8000/dash in your browser to access the web app

## Local Deployment
1) For running the webserver locally run `make server`

## Credits
- Ismael Montes
- Gustavo Rincon
- Mauricio J Diaz
- Juan C Pineda
- Martin Rodriguez
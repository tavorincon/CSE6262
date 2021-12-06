# CSE6242 Group Project


# Description
This repository contains the Docker images and application code required to deploy and run our group project. The group project is composed of a web application with three pages: Home, Historical Analysis & Officers Allocation.

# Installation 
## First steps
1) Clone this repository in your PC. For first timers, follow [these](https://www.jcchouinard.com/clone-github-repository-on-windows/) instructions.
2) Copy the `KCPD_Crime_Data_Complete.csv` file available [here](https://b.gatech.edu/3EsQa1M) into `data/crime`.
3) Copy the `init.sql` file available [here](https://b.gatech.edu/3EsQa1M) into `db/`.
4) Rename `.env-example` to `.env`. This file contains your environment configuration. The `.env` should not be commited to GitHub, since each developer / server using the application could require a different environment configuration. Furthermore, this would be a security risk, since any sensitive credentials would get exposed. Follow the "Obtain credentials tokens for .env file" instructions below to populate the .env file.

## Obtain credentials tokens for .env file
### Displaying maps
The project uses MapBox for obtaining the map tiles. You need to generate an [Access Token](https://account.mapbox.com/access-tokens/), then copy and paste it in the `.env` file. (You must sign-up for an account).

### Obtaining geoJSON boundaries
For displaying the ZIP Codes polygons we obtained the boundaries from a freemium API in RapidAPI. If you want to refresh the data you need to create an API key [here](https://rapidapi.com/VanitySoft/api/boundaries-io-1/), then copy and paste it in the `.env` file. (Make sure to Sign-up and Subscribe before copying access token).

## Deploying application

## Via Docker (RECOMMENDED METHOD)
Open a terminal (i.e. Git BASH on Windows, Terminal on Mac), navigate to the root of the cloned repository "CSE6242" and run `docker-compose up --build`.

# Execution
Once the containers has been started you may go to http://localhost:8000/dash in your browser to access the web app.


# Original Datasets & Prediction Results
The original datasets used to build this project can be found [here](https://data.kcmo.org/browse?limitTo=datasets&q=crime&sortBy=relevance&utf8=%E2%9C%93&page=1). In addition, the model prediction results  are available in the [Prophet Forecasting folder](https://b.gatech.edu/3EsQa1M)


## Credits
- Ismael Montes
- Gustavo Rincon
- Mauricio J Diaz
- Juan C Pineda
- Martin Rodriguez

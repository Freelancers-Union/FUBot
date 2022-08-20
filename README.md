# Freelancers Union Discord Bot

FUBot is a python Discord Bot built exclusively for the FU Discord.

# Commands

| Command                  | Description                                   | arguments            | Example                                  |
|--------------------------|-----------------------------------------------|----------------------|------------------------------------------|
| /player_card             | Gets information for a given player           | character_name       | /player_card `wrel`                      |
| /outfit                  | Gets information for a given Outfit           | [name] / [tag]       | /outfit `FU`                             |
| /announce_event          | Posts an announcement for an event            | event [message_body] | /announce_event `FUBG` `We're building!` |
| /new_member_report       | Posts to #officers new Discord members        | days                 | /new_member_report `30`                  |
| /link_planetside_account | Links PlanetSide 2 account to FU discord user | account_name         | /link_planetside_account `Karlish`       |



# Development

Utilises the [Auraxium](https://github.com/leonhard-s/auraxium) PS2 Census python wrapper.
[disnake](https://docs.disnake.dev/en/latest/index.html), a fork of discordpy.
[MongoDB](https://www.mongodb.com/) as a document database.

## Requirements

- [Python3](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/engine/install/)
- [A PS2 Census API service token](https://census.daybreakgames.com/#service-id)

## Getting Started
### Create a `.env` file


Create a `.env` file to store local env vars in the root of the project (This MUST be included in `.gitignore`)

```
LOGLEVEL=[DEBUG/INFO/WARNING/EXCEPTION]
DISCORDTOKEN= #This is a secret!
CENSUS_TOKEN=s:yourtoken # s:example will work but is limited to 10reqs/m
ENVIRONMENT=[dev/prod]
PORT_MAPPING=443:80
MONGO_DB_PORT_MAPPING=127.0.0.1:27017:27017 # This if running locally
MONGO_DATA_DIR=D:/var/lib/FUBot/mongodb # You can change this if required
MONGO_USERNAME=FUBot
MONGO_PASSWORD= #This is a secret but if running locally you can set your own

```
### Local
Docker is cool and all, but running it locally is much faster to develop with. You can use the package manager [pip](https://pip.pypa.io/en/stable/) to install `src/requirements.txt` and use the python-dotenv package to handle reading in env vars (you'll need to install this)

```bash

pip install -r ./src/requirements.txt
```
Run your bot 
```
python3 ./src/main.py

```
### Docker


Install [Docker](https://docs.docker.com/get-docker/) and start the Docker engine.

From the top level `FU/` directory, build the docker image using docker-compose:
```bash
docker-compose -d up
``` 

Check on your containers with:
```
docker logs fubot
docker logs mongodb
```

To stop your containers:
```
docker-compose down

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
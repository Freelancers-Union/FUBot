# Freelancers Union Discord Bot

FUBot is a python Discord Bot built exclusively for the FU Discord.

# Commands

| Command | Description  | arguments  | Example  |
| ------- | --- | --- | --- |
| /player_card | Gets information for a given player | character_name | /player_card `wrel` |
| /outfit | Gets information for a given Outfit | [name] / [tag] | /outfit `FU` |
| /announce_event | Posts an announcement for an event | event [message_body] | /announce_event `FUBG` `We're building!` |
| /new_member_report | Posts to #officers new Discord members | days | /new_member_report `30` |



# Development
Utilises the [Auraxium](https://github.com/leonhard-s/auraxium) PS2 Census python wrapper and [disnake](https://docs.disnake.dev/en/latest/index.html), a fork of discordpy.

## Requirements

- [Python3](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/engine/install/)
- [A PS2 Census API service token](https://census.daybreakgames.com/#service-id)

## Getting Started
### Create a `.env` file
Create a `.env` file to store local env vars (This MUST be included in `.gitignore`)

```
LOGLEVEL=DEBUG/INFO/WARNING/EXCEPTION
DISCORDTOKEN= #This is a secret!
CENSUS_TOKEN=<your PS2 census serivce ID> # s:example will work!
```
### Local
Docker is cool and all, but running it locally is much faster to develop with. You can use the package manager [pip](https://pip.pypa.io/en/stable/) to install `src/requirements.txt` and use the python-dotenv package to handle reading in env vars (you'll need to install this)

```bash
pip install -r path/to/fu/src/requirements.txt
```
Run your bot 
```
python3 /path/to/src/main.py
```
### Docker


Install [Docker](https://docs.docker.com/get-docker/) and start the Docker engine.

From the top level `FU/` directory, build the docker image using:
```bash
docker build -t fubot .
``` 

Run your bot using your local `.env` file:
```bash
docker run -d --name fubot --env-file .\src\.env fubot
```
Check on your container with:
```
docker logs fubot
expected output:
08/07/2022 12:57:32 PM on_ready: FUBot is ready!
```

To stop your container:
```
docker stop fubot
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
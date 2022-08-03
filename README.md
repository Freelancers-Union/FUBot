# Freelancers Union Discord Bot

FUBot is a python Discord Bot built exclusively for the FU Discord.

Utilises the [Auraxium](https://github.com/leonhard-s/auraxium) PS2 Census python wrapper and [disnake](https://docs.disnake.dev/en/latest/index.html), a fork of discordpy.

## Requirements

- Python3
- Docker

## Getting Started
Create a `.env` file to store env vars (make sure you add this to your `.gitignore` to avoid committing secrets!)

### Docker
The quickest and easiest way to get up and running is to use the Docker container.

Install [Docker](https://docs.docker.com/get-docker/) and start the Docker engine.

Everything can be run using docker-compose:
```bash
docker-compose up
``` 


### Local
You can use the package manager [pip](https://pip.pypa.io/en/stable/) to install `src/requirements.txt` and use the python-dotenv package to handle reading in env vars.

```bash
pip install -r src/requirements.txt
```
The project is made to be run from root folder of repository
MongoDB can be run locally using `docker-compose up mongodb`


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
# Freelancers Union Discord Bot

FUBot is a python Discord Bot built exclusively for the FU Discord.

Utilises the [Auraxium](https://github.com/leonhard-s/auraxium) PS2 Census python wrapper and [disnake](https://docs.disnake.dev/en/latest/index.html), a fork of discordpy.

## Requirements

- Python3
- Docker

## Getting Started
### Docker
The quickest and easiest way to get up and running is to use the Docker container.

Install [Docker](https://docs.docker.com/get-docker/) and start the Docker engine.

From the top level `FU/` directory, build the docker image using:
```bash
docker build -t fubot .
``` 
Create a `.env` file to store env vars (make sure you add this to your `.gitignore` to avoid committing secrets!)
```bash
docker run --env-file src/.env fubot
```

### Local
Alternatively, you can use the package manager [pip](https://pip.pypa.io/en/stable/) to install `src/requirements.txt` and use the python-dotenv package to handle reading in env vars.

```bash
pip install -r src/requirements.txt
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
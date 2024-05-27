# StellarBot


# Welcome to StellarBot
![stellarbot](stellarbot.webp)

[![Upload Python Package](https://github.com/nguemechieu/stellarbot/actions/workflows/python-publish.yml/badge.svg)](https://github.com/nguemechieu/stellarbot/actions/workflows/python-publish.yml)
[![Docker Image CI](https://github.com/nguemechieu/stellarbot/actions/workflows/docker-image.yml/badge.svg)](https://github.com/nguemechieu/stellarbot/actions/workflows/docker-image.yml)
[![Continuous Integration Workflow](https://github.com/nguemechieu/stellarbot/actions/workflows/continuous-integration-workflow.yml/badge.svg)](https://github.com/nguemechieu/stellarbot/actions/workflows/continuous-integration/workflow.yml)

## Description

StellarBot is a professional trading bot for the Stellar Network digital ledger. It allows you to execute trades on your own Stellar network using the standard protocol within the Stellar ecosystem. For more information on the Stellar Network, visit [Stellar Expert](https://stellar.expert/explorer/public/network-activity

Sure! Here is a detailed installation procedure for the Python application StellarBot:

# Installation Procedure for StellarBot

## Prerequisites

Before installing StellarBot, ensure you have the following prerequisites:

1. **Python 3.9 or higher**: Download and install Python from the [official Python website](https://www.python.org/downloads/).
2. **Git**: Download and install Git from the [official Git website](https://git-scm.com/downloads).
3. **Docker** (optional): If you prefer using Docker, download and install Docker from the [official Docker website](https://www.docker.com/get-started).

## Step-by-Step Installation

### Step 1: Clone the Repository

First, clone the StellarBot repository from GitHub to your local machine.

```bash
git clone https://github.com/nguemechieu/stellarbot.git
cd stellarbot
```

### Step 2: Create and Activate a Virtual Environment

It is recommended to use a virtual environment to manage dependencies. Create and activate a virtual environment using the following commands:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Dependencies

With the virtual environment activated, install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### Step 4: Configure StellarBot

Create a configuration file for StellarBot. You can use the provided sample configuration file as a template:

```bash
cp config.sample.json config.json
```

Edit the `config.json` file with your preferred settings.

### Step 5: Run StellarBot

After configuring StellarBot, you can start the application using the following command:

```bash
python stellarbot.py
```

### Step 6: Using Docker (Optional)

If you prefer running StellarBot using Docker, follow these steps:

1. Build the Docker image:

    ```bash
    docker build -t stellarbot .
    ```

2. Run the Docker container:

    ```bash
    docker run -d --name stellarbot stellarbot
    ```

## Additional Commands

- **Start StellarBot**: To start the bot.
  ```bash
  python stellarbot.py start
  ```

- **Stop StellarBot**: To stop the bot.
  ```bash
  python stellarbot.py stop
  ```

- **Check Status**: To check the current status of the bot.
  ```bash
  python stellarbot.py status
  ```

## Troubleshooting

If you encounter any issues during installation or while running StellarBot, please refer to the [issue tracker](https://github.com/nguemechieu/stellarbot/issues) on GitHub for assistance.



This installation procedure should help users set up and run StellarBot on their local machine. Feel free to adjust any specific details to match the actual configuration and setup requirements of StellarBot.

### Using Docker

To pull the Docker image and run StellarBot, use the following commands:

```sh
docker pull nguemechieu/stellarbot:latest
docker run -d --name stellarbot nguemechieu/stellarbot:latest
```

## Commands

Here are some basic commands to get started with StellarBot:

- `start`: Starts the trading bot.
- `stop`: Stops the trading bot.
- `status`: Shows the current status of the bot.

For a complete list of commands, refer to the [Commands Documentation](docs/commands.md).

## Links

- [Homepage](https://github.com/nguemechieu/stellarbot)
- [Documentation](docs/README.md)
- [Issues](https://github.com/nguemechieu/stellarbot/issues)
- [Stellar Network Activity](https://stellar.expert/explorer/public/network-activity)

## License

StellarBot is licensed under the [GPLv3 License](LICENSE).

## Contributing

Contributions are welcome! Please read the [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

## Contact

For any inquiries, please contact [nguemechieu@live.com](mailto:nguemechieu@live.com).

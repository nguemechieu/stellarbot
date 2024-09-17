
# StellarBot

## ------------- Your gateway to financial freedom -------------------------
[![Upload Python Package](https://github.com/nguemechieu/stellarbot/actions/workflows/python-publish.yml/badge.svg)](https://github.com/nguemechieu/stellarbot/actions/workflows/python-publish.yml)
[![Docker Image CI](https://github.com/nguemechieu/stellarbot/actions/workflows/docker-image.yml/badge.svg)](https://github.com/nguemechieu/stellarbot/actions/workflows/docker-image.yml)
[![Continuous Integration Workflow](https://github.com/nguemechieu/stellarbot/actions/workflows/continuous-integration-workflow.yml/badge.svg)](https://github.com/nguemechieu/stellarbot/actions/workflows/continuous-integration-workflow.yml)

## About StellarBot


StellarBot is a professional trading bot for the Stellar Network digital ledger. It allows you to execute trades on your own Stellar network using the standard protocol within the Stellar ecosystem. For more information on the Stellar Network, visit [Stellar Expert](https://stellar.expert/explorer/public/network-activity)

![StellarBot](https://github.com/nguemechieu/stellarbot/tree/master/src/assets)

## Installation Guide

### Prerequisites

Ensure you have the following prerequisites installed before setting up StellarBot:

- **Python 3.9+**: [Download here](https://www.python.org/downloads/).
- **Git**: [Install Git](https://git-scm.com/downloads).
- **Docker** (optional): [Get Docker](https://www.docker.com/get-started) for containerized deployment.

### Step-by-Step Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/nguemechieu/stellarbot.git
   cd stellarbot
   ```

2. **Set Up a Virtual Environment:**
   Create and activate a virtual environment for dependency management:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   Install required dependencies via `pip`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure StellarBot:**
   Copy the sample configuration and customize it to your preferences:
   ```bash
   cp config.sample.json config.json
   ```

5. **Run StellarBot:**
   Start StellarBot using:
   ```bash
   python stellarbot.py
   ```

---

### Docker Installation (Optional)

1. **Build the Docker Image:**
   ```bash
   docker build -t stellarbot .
   ```

2. **Run the Docker Container:**
   ```bash
   docker run -d --name stellarbot stellarbot
   ```

---

## Commands

- **Start the bot**: 
  ```bash
  python stellarbot.py start
  ```
- **Stop the bot**:
  ```bash
  python stellarbot.py stop
  ```
- **Check the bot’s status**:
  ```bash
  python stellarbot.py status
  ```

For more commands, check the [Commands Documentation](docs/commands.md).

---

## Troubleshooting

If you encounter any issues during installation or while running StellarBot, please visit the [issue tracker](https://github.com/nguemechieu/stellarbot/issues) for support.

---

## Using Docker

For a containerized approach, pull the latest image and run StellarBot as a Docker container:

```bash
docker pull nguemechieu/stellarbot:latest
docker run -d --name stellarbot nguemechieu/stellarbot:latest
```

---

## Resources and Links

- [StellarBot Repository](https://github.com/nguemechieu/stellarbot)
- [Documentation](docs/README.md)
- [Issue Tracker](https://github.com/nguemechieu/stellarbot/issues)
- [Stellar Network Activity](https://stellar.expert/explorer/public/network-activity)

---

## License

StellarBot is released under the [GPLv3 License](LICENSE).

---

## Contributing

We welcome contributions! Please read the [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

---

## Contact

For further inquiries, reach out at [nguemechieu@live.com](mailto:nguemechieu@live.com).

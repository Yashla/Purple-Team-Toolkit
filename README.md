# Purple Team Toolkit Docker Container Setup

## Prerequisites

Before you start using this Docker container, ensure that you have the necessary packages installed on your system:

```bash
sudo apt update && sudo apt install curl
```

## Installation

Install Docker and Docker Compose with the following command:

```bash
curl -fsSL https://get.docker.com/ -o get-docker.sh && sudo sh get-docker.sh && sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose
```

## Network Configuration

Modify the IP address settings in `docker-compose.yml` to match your specific network configuration requirements. Once done, configure the Docker network by typing the following commands:

```bash
docker network create -d macvlan   --subnet=192.168.0.0/24 \ # Change as needed
  --gateway=192.168.0.1 \   # Change as needed
  -o parent=ens37 pub_net   # Change as needed
```

### Steps:
1. Open your `docker-compose.yml` file.
2. Modify the IP address and network settings as required for your setup.
3. Run the above command to create a Docker network.

## Running the Container

To start the Docker container:

```bash
docker-compose up
```

To stop the Docker container:

```bash
docker-compose down
```

Please ensure all IP addresses and network configurations are correctly set up in `docker-compose.yml` before starting the container.


### Browse the Purple Team Toolkit on the IP address you configured.

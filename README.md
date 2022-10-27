# mqtt-sps-bridge

Sample implementation of an Thing Interface after TASMI Specification.

The SPS part is only working with our Project Container Crane. If you want to use a other thing, you need to change the corrosponding code. 

TODO: how to modifify for other SPS

## How to setup



### Prerequisites

#### MQTT Broker

If you want to send thing positions to SAND and get alerts from SAND than you need a mqtt broker.
You need an mqtt broker like [mosquitto](https://mosquitto.org/). 

#### System Dependencies

tbd

### Development setup

If you only want to use the mqtt-sps-bridge directly, you can skip this section. Although we
can very much recommend `poetry` in general for your own python projects.

We use `poetry` to manage our dependencies. To install `poetry` you can use
[(more infos here)](https://python-poetry.org/docs/):
```shell
$ curl -sSL https://install.python-poetry.org | python -
```

Our dependencies are documented in the [pyproject.toml](pyproject.toml), the
explicit versions with hashes for the libraries you can find in
[poetry.lock](poetry.lock).


### Installation

```shell
$ poetry install
```

## Usage

All IPs defaults to ``localhost / 127.0.0.1``.

```shell
$ python src/bridge/main.py --ccs --sand
```

If you want to start our local development SPS Server:

```shell
$ python src/bridge/main.py --ccs --sand --server
```

If the mqtt broker and sps are on different IPs:

```shell
$ python src/bridge/main.py --ccs --sand --mqttip 123.123.123.123 --spsip 111.111.111.11
```

#### Long-term System

If you want to run install it on the actual system where it should run
long-term, we opted for a systemd-service to make starting/stopping very easy
and also the logging gets easier. You probably still want to adapt it slightly
to use your specific config or use additional links to match the default config
name. You find the systemd file in this repository, it will not come bundled in
the python artifact.

Installation:
```shell
# cd /etc/systemd/system
# ln -s /path/to/sand/sand.service .
```

After that you can start/stop it via:
```shell
# systemctl start sand
```

Also the logs on the INFO-Level are routed through the journal, which is why you
can also read most of the logs via:
```shell
# journalctl -u sand
```

## Roadmap

This project has no roadmap. It is just a reference/example implementation.


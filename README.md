# Zoe madtrans ![Agent version](https://img.shields.io/badge/Zoe_Agent-0.1.0-blue.svg "Zoe madtrans")

Dynamic information on the transportation in Madrid.

## Requirements

The `requests` library is automatically installed by the `postinst` script.

Before the agent can perform requests to the EMT API, you must register in
[their webpage](opendata.emtmadrid.es/) in order to obtain an user
identification and password key.

After obtaining those, simply add the **user identification** in the first line
of the `ZOE_HOME/etc/madtrans.conf` file and the **password key** in a new line
after that.

(Re)start the agent and you are ready to go.

## Functionality

Right now, this agent provides some of the functions from the API related to
bus transport (stops, lines, waiting times, etc.)

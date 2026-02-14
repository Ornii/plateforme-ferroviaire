# Traffic-light-with-web-command
Control a traffic light between two separate computers with a website.

## Requirements:
Install Flask and pyyaml via `pip install flask` and `pip install pyyaml`.

## Usage:

Get your local IPV4 address via `ipconfig` and put it on client\config.yaml. 
Then run client\main.py and server\main.py (with 1 or 2 computers). Each client is defined with a separate folder

The website address is [0.0.0.0:8080](http://0.0.0.0:8080/) by default on the computer which runs server\main.py.

# CMG-365-Widgets

## About
This repository contains an application to automate quality control evaluation for 365-Widgets products such as 
thermometers, humidity sensons and so on.

The application process content of a log file, evaluate quality of a sensors and write their classification to 
the standard output as well as json file.

Contains python application, config files to build and run application in a Docker container (Dockerfile, docker-compose)
and Kubernetes resources to deploy and run the application in Kubernetes cluster.

## Proposals
- input log file could be split per sensor to allow easier input data manipulation

## TODO list
Missing features are:
- Kubernetes resources packaged in helm chart
- IaC configuration (ex. Terraform, AWS CloudFormation)

## Usage
Application can be used several ways:
1. execute python application
2. build and run Docker container manually
3. build and run Docker container with docker-compose
4. deploy and run application in Kubernetes cluster

### Python
Application expects to pass a function `parse` followed by path to log file, optionally you can pass also output file.

Note: Empty line in the log file cause end of the application!

```
$ python3 ./app/parse_log.py -h
usage: parse_log.py [-h] [-o OUTPUT] function log

Read the log file, parse its content and save the results in a file.

positional arguments:
  function              parse
  log                   path to the log file to parse

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file to export (default: output.json)
```

```
python3 ./app/parse_log.py parse ./logs/example.log
python3 ./app/parse_log.py parse ./logs/example2.log -o output2.log
```

Example:
```
$ python3 ./app/parse_log.py parse ./logs/example.log
File ./logs/example.log will be parsed and exported to output.json
Test room reference values:
     temperature:    70.0 degrees
     humidity:       45.0 %

Thermometer temp-1 registered.
Thermometer temp-1 is 'precise'.

Thermometer temp-2 registered.
Thermometer temp-2 has standard deviation 0.9044335243676014 and is 'ultra precise'.

Humidity sensor hum-1 registered.
Humidity sensor hum-1 has 0 deviatations. Will be kept.

Humidity sensor hum-2 registered.
Humidity sensor hum-2 has 4 deviatations. Will be discarded.

Output: 
{
  "temp-1": "precise",
  "temp-2": "ultra precise",
  "hum-1": "keep",
  "hum-2": "discard"
}
$ cat output.json
{
  "temp-1": "precise",
  "temp-2": "ultra precise",
  "hum-1": "keep",
  "hum-2": "discard"
}$
```

### Docker
To build a docker image run following command:
```
$ docker build -t parse-log .
... ommitted ...
```

Executing the container without any parameter will print the help:
```
$ docker run --rm parse-log
usage: parse_log.py [-h] [-o OUTPUT] function log

Read the log file, parse its content and save the results in a file.

positional arguments:
  function              parse
  log                   path to the log file to parse

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file to export (default: output.json)
$
```

In order to parse and evaluate sensors you need to pass a `parse` function and specify an input log file. 
Optionally you can change the default output file.
If you want to access the output file on host machine, you need to mount a volume and specify local user.

```
$ docker run --rm -v $PWD/:/opt/parse_log -u 1000 parse-log parse ./logs/example2.log -o test2.json
File ./logs/example2.log will be parsed and exported to test2.json
Test room reference values:
     temperature:    72.0 degrees
     humidity:       44.5 %

Thermometer temp-1 registered.
Thermometer temp-1 is 'precise'.

Thermometer temp-2 registered.
Thermometer temp-2 is 'precise'.

Humidity sensor hum-1 registered.
Humidity sensor hum-1 has 3 deviatations. Will be discarded.

Humidity sensor hum-2 registered.
Humidity sensor hum-2 has 3 deviatations. Will be discarded.

Thermometer temp-3 registered.
Thermometer temp-3 has standard deviation 0.7277820186475215 and is 'ultra precise'.

Humidity sensor hum-3 registered.
Humidity sensor hum-3 has 0 deviatations. Will be kept.

Thermometer temp-4 registered.
Thermometer temp-4 has standard deviation 3.1246818019818194 and is 'very precise'.

Output: 
{
  "temp-1": "precise",
  "temp-2": "precise",
  "hum-1": "discard",
  "hum-2": "discard",
  "temp-3": "ultra precise",
  "hum-3": "keep",
  "temp-4": "very precise"
}
$
```

### docker-compose
1. Set the values for `command` in `docker-compose.yaml`
2. Execute `docker-compose up`

Note: You need to pass environmental variables `UID` to specify local user to be able to write output file to the 
host machine. See example below.

```
$ env UID=${UID} docker-compose up
Recreating parse-log ... done
Attaching to parse-log
parse-log    | File ./logs/example.log will be parsed and exported to test.json
parse-log    | Test room reference values:
parse-log    |      temperature:    70.0 degrees
parse-log    |      humidity:       45.0 %
parse-log    | 
parse-log    | Thermometer temp-1 registered.
parse-log    | Thermometer temp-1 is 'precise'.
parse-log    | 
parse-log    | Thermometer temp-2 registered.
parse-log    | Thermometer temp-2 has standard deviation 0.9044335243676014 and is 'ultra precise'.
parse-log    | 
parse-log    | Humidity sensor hum-1 registered.
parse-log    | Humidity sensor hum-1 has 0 deviatations. Will be kept.
parse-log    | 
parse-log    | Humidity sensor hum-2 registered.
parse-log    | Humidity sensor hum-2 has 4 deviatations. Will be discarded.
parse-log    | 
parse-log    | Output: 
parse-log    | {
parse-log    |   "temp-1": "precise",
parse-log    |   "temp-2": "ultra precise",
parse-log    |   "hum-1": "keep",
parse-log    |   "hum-2": "discard"
parse-log    | }
parse-log exited with code 0
$
$ docker-compose down
Removing parse-log ... done
Removing network cmg-365-widgets_default
$
```

### Kubernetes
Apply manifest for pod or deployment against Kubernetes cluster:
```
$ kubectl apply -f k8s/deployment.yaml
```

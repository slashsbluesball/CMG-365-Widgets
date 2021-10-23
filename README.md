# CMG-365-Widgets

## Usage

```
$ python3 parse_log.py parse ../logs/example.log
$ python3 parse_log.py parse ../logs/example2.log -o output2.json
```

```
docker build -t parse-log .
docker run --rm -v $PWD/:/opt/parse_log -u 1000 parse-log parse ./logs/example2.log -o test.json
```

```
env UID=${UID} GID=${GID} docker-compose up
```

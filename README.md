# iR(acing) Team Dashboard

## To Do

* Monitor active websocket clients to the web app.

## Agent Installation (Windows / from sources)

1. Install Python 3.
2. Download the source code repository as a zip.
    * https://github.com/lanmaster53/ir-team-dashboard/archive/refs/heads/main.zip
3. Unzip the archive.
4. Open a command prompt and navigate to the ...\ir-team-dashboard\iragent directory.
5. Create a virtual environment.
    * `python -m venv .venv`
6. Activate the virtual environment.
    * `.venv\Scripts\activate.bat`
7. Install dependencies.
    * `pip3 install -r REQUIREMENTS.txt`
8. Set the proper environment variables.
    * `set API_BASE_URL=<server_url>`
9. Run the agent.
    * `python iragent.py`

## Server Installation (Linux / Docker)

1. Create and configure a Google Cloud Compute Engine instance.
    * Use the Container-Optimized OS.
        * Allow HTTP.
    * Configure remote SSH.

2. On the remote system, clone the iR Team Dashboard repository.

```
$ git clone https://github.com/lanmaster53/ir-team-dashboard.git
```

3. Build the iR Team Dashboard Docker image.

```
$ cd ir-team-dashboard
$ docker build --rm -t irteamdash .
```

4. Launch the server manager via Docker.

```
$ docker run -d --rm --name irteamdash \
    -v $PWD:/irteamdash \
    -p 80:5000 \
    -e API_BASE_URL="<server_url>" \
    irteamdash \
    gunicorn --bind 0.0.0.0:5000 --worker-class eventlet --workers 1 irteamdash.wsgi:app --error-logfile gunicorn-irteamdash.log --log-level DEBUG
```

Use the following command to attach to the container. A container cannot be detached from unless the container was created with the `-it` switch. If so, then the `ctrl-p` `ctrl-q` sequence will safely detach from the container without causing it to exit.

```
$ docker attach irteamdash
```

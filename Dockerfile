FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV APP_USER=appuser
ENV APP_BASE=/opt/parse_log
# ENV LOG_FILE=${LOG_FILE}
# ENV OUTPUT_FILE=${OUTPUT_FILE:-"output.json"}

# Install pip requirements
# COPY requirements.txt .
# RUN python -m pip install -r requirements.txt

WORKDIR ${APP_BASE}

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" ${APP_USER} && chown -R ${APP_USER} ${APP_BASE}
USER ${APP_USER}:${APP_USER}

COPY --chown=${APP_USER}:${APP_USER} . ${APP_BASE}

ENTRYPOINT [ "python", "./app/parse_log.py" ]
CMD [ "-h" ]

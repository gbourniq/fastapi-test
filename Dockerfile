FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

LABEL author="Guillaume Bournique <gbournique@gmail.com>"

ARG USERNAME="fastuser"
ENV REPO_HOME="/home/${USERNAME}" \
    PYTHONPATH="/home/${USERNAME}" \
    USERNAME=${USERNAME}

# Add non-root user
RUN adduser --disabled-password --gecos "" ${USERNAME}

# Set working directory
WORKDIR ${REPO_HOME}

# Copy dependencies files
COPY poetry.lock pyproject.toml ./

# Install poetry and app dependencies
RUN pip install "poetry==1.1.0b2" \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && rm poetry.lock pyproject.toml

# Add project source code to /home/portfolio
COPY ./veryneatapp ./veryneatapp/

# Inform Docker the app will be exposed on port 80
EXPOSE 5700

# Change ownership of /home/portfolio to portfoliouser
RUN chown -R ${USERNAME}:${USERNAME} ${REPO_HOME}

# Set default user to be non-root user
USER $USERNAME
ARG VIRTUAL_ENV_NAME=dcs-minimal
ARG VIRTUAL_ENV=/databricks/python3
ARG ASOS_INDEX_URL
ARG ASOS_AI_RETSCI_KEY
ARG DATABRICKS_HOST
ARG DATABRICKS_TOKEN
ARG MLFLOW_TRACKING_URI



FROM databricksruntime/python:9.x as promotheus-databricks-builder
ARG VIRTUAL_ENV
ARG ASOS_INDEX_URL

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 git

# Set environment
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Setup ASOS private PyPI
RUN touch pip.conf && \
    echo "[global]" >> pip.conf && \
    echo "extra-index-url=${ASOS_INDEX_URL}" >> pip.conf
ENV PIP_CONFIG_FILE pip.conf

# Install prod packages
COPY requirements.txt .
RUN $VIRTUAL_ENV/bin/pip install -r requirements.txt
RUN rm -f pip.conf




# 'Prod' image simulating Databricks runtime environment for jobs
FROM databricksruntime/python:9.x as promotheus-databricks
ARG ASOS_INDEX_URL
ARG ASOS_AI_RETSCI_KEY
ARG MLFLOW_TRACKING_URI

# TODO: Does LightGBM break without this?
# # Install dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends libgomp1

# Transfer virtualenv
COPY --from=promotheus-databricks-builder /databricks/python3 /databricks/python3

ENV ASOS_INDEX_URL=${ASOS_INDEX_URL}
ENV ASOS_AI_RETSCI_KEY=${ASOS_AI_RETSCI_KEY}
ENV MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI}

# @SECURITY: This image does not switch to a non-root user because that's Databrick's remit




FROM asnpairetsciacr.azurecr.io/promotheus/databricks:latest as promotheus-base
ARG VIRTUAL_ENV
ARG ASOS_INDEX_URL
ARG DATABRICKS_HOST
ARG DATABRICKS_TOKEN

WORKDIR /

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends -y wget git build-essential && \
    git clone https://github.com/google/jsonnet.git && cd jsonnet && make

# Set environment
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Setup ASOS private PyPI access
RUN touch pip.conf && \
    echo "[global]" >> pip.conf && \
    echo "extra-index-url=${ASOS_INDEX_URL}" >> pip.conf
ENV PIP_CONFIG_FILE pip.conf
RUN pip install --upgrade pip

# Configure Databricks CLI
# @SECURITY: To avoid creds in cleartext files, switch to using env vars directly when dbx cli supports them
RUN echo "Generating [~/.databrickscfg]" && \
    touch ~/.databrickscfg && \
    echo "[DEFAULT]" >> ~/.databrickscfg && \
    echo "host = $DATABRICKS_HOST" >> ~/.databrickscfg && \
    echo "token = $DATABRICKS_TOKEN" >> ~/.databrickscfg && \
    echo "" >> ~/.databrickscfg

WORKDIR /mnt/src
ENV PYTHONPATH="$PYTHONPATH:."




# Base image for common automation tooling
FROM asnpairetsciacr.azurecr.io/promotheus/base:latest as promotheus-shell
ARG VIRTUAL_ENV
ARG ASOS_INDEX_URL
ARG DATABRICKS_HOST
ARG DATABRICKS_TOKEN

WORKDIR /

# Install orchestration packages
COPY requirements.txt requirements.shell.txt ./
RUN /databricks/python3/bin/pip install -r requirements.shell.txt

# # TODO @SECURITY: Create and switch to non-root user




# 'Dev' image enhanced for interactive usage
FROM asnpairetsciacr.azurecr.io/promotheus/base:latest as promotheus-dev
ARG VIRTUAL_ENV
ARG ASOS_INDEX_URL
ARG DATABRICKS_HOST
ARG DATABRICKS_TOKEN

WORKDIR /

# Install dev packages
COPY requirements.txt requirements.dev.txt ./
RUN /databricks/python3/bin/pip install -r requirements.dev.txt

# Improve shell usability
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.1/zsh-in-docker.sh)" -- \
    -a "source activate ${VIRTUAL_ENV_NAME}"
COPY ./.p10k.zsh $USER/.p10k.zsh
RUN sed -i '/POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS/d' ~/.zshrc && \ 
    echo "POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(virtualenv)" >> ~/.zshrc && \
    echo "[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh" >> ~/.zshrc

# # TODO @SECURITY: Create and switch to non-root user

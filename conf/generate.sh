#!/bin/bash

echo "Generating deployment config from template..."
/jsonnet/jsonnet \
    --ext-str "PIP_EXTRA_INDEX_URL=$ASOS_INDEX_URL" \
    --ext-str "ASOS_AI_RETSCI_KEY=$ASOS_AI_RETSCI_KEY" \
    --ext-str "PROMOTHEUS_ENV=$PROMOTHEUS_ENV" \
    --ext-str "DATABRICKS_HOST=$DATABRICKS_HOST" \
    --ext-str "DATABRICKS_TOKEN=$DATABRICKS_TOKEN" \
    conf/deployment.jsonnet -o conf/deployment.json
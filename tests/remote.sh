#!/bin/bash

./conf/generate.sh
dbx deploy --jobs=promotheus-test --files-only
dbx launch --job=promotheus-test --as-run-submit --trace | tee output.txt
if grep -q 'result state: SUCCESS' output.txt
then 
    echo "Remote integration tests successful."
    exit 0
else
    echo "Remote integration tests failed. Check Databricks logs for details."
    exit 1
fi
./conf/cleanup.sh

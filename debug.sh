#!/usr/bin/env bash

set -e

quilt3 logout
mkdir -p quilt-tmp
echo "QUILT-DEBUG: Cloning debugger script repo"
git clone https://github.com/quiltdata/debugging-scripts quilt-tmp/debugging-scripts
cd quilt-tmp
echo "QUILT-DEBUG: ls after cd quilt-tmp/"
ls
echo "QUILT-DEBUG: Running python code that debugs"
python package_deletion_problem.py > quilt-pkg-delete-debug.log 2> /dev/null
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo ${TIMESTAMP}
AWS_ACCESS_KEY_ID=${QUILT_DEBUG_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY=${QUILT_DEBUG_SECRET_ACCESS_KEY} AWS_REGION=us-east-1 aws s3 cp quilt-pkg-delete-debug.log s3://quilt-support/hudl/${TIMESTAMP}/quilt-pkg-delete-debug.log
cd ..
# rm -rf ./quilt-tmp/
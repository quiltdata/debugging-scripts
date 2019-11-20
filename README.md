# Debugging Package Deleting Failure

First, set up your environment the way you normally run quilt. The debug code expects to be able to make boto3 calls and it expects that quilt3 is installed.

For me, this would be activating a virtual environment and exporting AWS_PROFILE=myprofile. You may not need to do anything.

After that 
```
export QUILT_DEBUG_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXXX
export QUILT_DEBUG_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXX
export QUILT_DEBUG_BUCKET=XXXXXXX

curl https://raw.githubusercontent.com/quiltdata/debugging-scripts/master/debug.sh -o debug.sh && chmod +x debug.sh && ./debug.sh
```

To cleanup:
```
rm debug.sh
rm quilt-pkg-delete-debug.log
```


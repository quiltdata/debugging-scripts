# Debugging Package Deleting Failure

```
export QUILT_DEBUG_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXXX
export QUILT_DEBUG_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXX
export QUILT_DEBUG_BUCKET=XXXXXXX

curl https://raw.githubusercontent.com/quiltdata/debugging-scripts/master/debug.sh -o debug.sh && chmod +x debug.sh && ./debug.sh

rm debug.sh
rm quilt-pkg-delete-debug.log
```


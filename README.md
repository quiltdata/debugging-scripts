# Debugging Package Deleting Failure

```
export QUILT_DEBUG_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXXX
export QUILT_DEBUG_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXX
curl https://raw.githubusercontent.com/quiltdata/debugging-scripts/hudl/debug.sh -o debug.sh && chmod +x debug.sh && ./debug.sh

rm debug.sh
sudo rm -r quilt-tmp/
```
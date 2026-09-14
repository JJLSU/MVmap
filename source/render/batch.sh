#!/bin/sh
# batch.sh which n start budget_seconds : render strips from start while time remains
which=$1; n=$2; i=$3; budget=$4; t0=$(date +%s)
while [ $i -lt $n ]; do
  if [ -f strips/$which-$(printf %02d $i).png ]; then i=$((i+1)); continue; fi
  now=$(date +%s); elapsed=$((now-t0)); [ $elapsed -gt $budget ] && break
  python3 strip.py $which $i $n 2>&1 | grep "STRIP DONE"
  i=$((i+1))
done
ls strips | tr '\n' ' '

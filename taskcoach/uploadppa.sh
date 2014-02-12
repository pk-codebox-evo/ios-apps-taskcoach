#!/bin/bash

for versionName in lucid precise quantal raring saucy; do
    for retryCount in 1 2 3 4 5 6 7 8 9 10; do
	make ${1}_$versionName && break || exit 1
    done
done

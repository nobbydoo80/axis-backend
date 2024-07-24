#!/bin/sh

for file in $(ls *.csv); do
  (head -n 2 ${file} && tail -n +3  ${file} | sort -fd) > newfile
  mv newfile ${file}
done

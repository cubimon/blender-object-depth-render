#!/bin/bash
find . -type d -regex "./[0-9]*" -exec rm -r {} \;

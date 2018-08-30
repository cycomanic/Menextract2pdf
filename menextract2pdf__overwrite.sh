#!/bin/sh
# Helps to find the right mendeley.sqlite-DB

mendeleydb="$(ls "$1"/*www.mendeley.com.sqlite)"
python menextract2pdf.py "$mendeleydb" "$2" --overwrite
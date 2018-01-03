#!/bin/bash
shopt -s extglob
echo "This script will permanently delete the usedcars.db database
and permanently delete the image files in static/uploads."
echo ""
read -r -p "Are you sure you want to delete these? [y/N] " response
response=${response,,}
if [[ "$response" =~ ^(yes|y)$ ]]
then
    rm -rf usedcars.db
    rm -rf static/uploads/!(placeholder.png)
    echo "DB destroyed!"
else
    echo "Maybe next time!"
fi
#!/bin/bash

# This script builds the project and copies the resulting ./dist folder to the server

# check if working in root directory, both client and server folders should be present
if [ ! -d "client" ] || [ ! -d "server" ]; then
    echo "Please run this script from the root directory of the Repo"
    exit 1
fi

# build the project
# Go into the client folder and build the project using yarn
cd client
yarn install
yarn build

# Go back to the root directory
cd ..

# copy the dist folder to the server
# Go into the server folder, remove the old static folder and copy the new dist folder, copy index.html to templates
echo "Copying the generated files to the server"
cd server/chainfury_server/
if [ -d "static" ]; then
    echo "Removing old static folder"
    rm -rf static
fi

mkdir static
cp -r ../../client/dist/. static/.

# Go back to the root directory
cd ../..

# Done
echo "Done"
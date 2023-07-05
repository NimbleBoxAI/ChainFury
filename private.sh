cd client
yarn install
yarn build
cd ..

echo "Copying built files to the server static folder ..."
cp -r client/dist/ server/static/
mkdir -p ./server/templates
cp ./client/dist/index.html ./server/templates/index.html
echo "Done!"
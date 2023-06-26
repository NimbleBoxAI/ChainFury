cd client
yarn install
yarn build
cd ..

cp -r client/dist/ server/static/
mkdir -p ./server/templates
cp ./client/dist/index.html ./server/templates/index.html
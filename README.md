# ChainFury

<img src="./docs/clock.png" align="center"/>


ChainFury is a powerful tool that simplifies the creation and management of chains of prompts, making it easier to build complex chat applications using LLMs. With a simple GUI inspired by [LangFlow](https://github.com/logspace-ai/langflow)), ChainFury enables you to chain components of [LangChain](https://github.com/hwchase17/langchain) together, allowing you to embed more complex chat applications with a simple JS snippet.

You can try out ChainFury [here](https://alpaca-irregulardensity.byocawsv0.on.nimblebox.ai/).


## Featues
ChainFury supports a range of features, including:

- Recording all prompts and responses and storing them in a database
- Collecting metrics like latency to provide an easy-to-use scoring mechanism for end-users
- Querying OpenAI's API to obtain a rating for the response, which it stores in the database.

The components currently supported by ChainFury include:
- LLMs and Prompts 📃
- Chains 🔗
- Data Augmented Generation 📚
- Agents 🤖
- Memory 🧠
- Evaluation 🧐

## Installation

Installing ChainFury is easy, with two methods available.

### **Method 1: Docker**

The easiest way to install ChainFury is to use Docker. You can use the following command to run ChainFury:

```bash
docker build . -f Dockerfile -t chainfury:latest

docker run --env OPENAI_API_KEY=<your_key_here> -p 8000:8000 chainfury:latest
```

### **Method 2: Manual**

For this, you will need to build the frontend and and then run the backend. The frontend can be built using the following command:

```bash
cd client
yarn install
yarn build
```

To copy the frontend to the backend, run the following command:

```bash
cd ..
cp -r client/dist/ server/static/
cp ./client/dist/index.html ./server/templates/index.html
```

Now you can install the backend dependencies and run the server. We recommend using Python 3.9 virtual environment for this:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd server
uvicorn app:app --log-level=debug --host 0.0.0.0 --port 8000 --workers 1

```

### Contributing
ChainFury is a work in progress, and is currently in the alpha stage. Please feel free to contribute to the project!


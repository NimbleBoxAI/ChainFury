# first stage is to build the client
FROM node:16-alpine3.14 as builder
WORKDIR /app
COPY ./client/package*.json ./client/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY ./client .
RUN yarn build
ENV NODE_ENV production

# then we copy over the server
FROM python:3.9
RUN mkdir /app

# # this is copying over the chainfury engine and install it
COPY ./chainfury /app/chainfury
COPY pyproject.toml /app
COPY README.md /app
WORKDIR /app
RUN python3 -m pip install .
RUN python3 -m pip install PyMySQL
WORKDIR /

# copy over the server files including the server installer, since chainfury is already installed
# it would use the cached version and not try to install it again from pypi
COPY ./server/chainfury_server /app/chainfury_server
COPY ./server/pyproject.toml /app
COPY ./server/README.md /app
WORKDIR /app
RUN python3 -m pip install -e .
# RUN python3 -m pip install --no-deps langflow==0.0.89
WORKDIR /

# Copy over the files from the client build
RUN rm -rf /app/static
RUN rm -rf /app/templates
COPY --from=builder /app/dist/. /app/chainfury_server/static/.

WORKDIR /app/chainfury_server
EXPOSE 8000
CMD ["python3", "server.py", "--host", "0.0.0.0", "--port", "8000"]

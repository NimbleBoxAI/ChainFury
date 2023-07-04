FROM node:16-alpine3.14 as builder
WORKDIR /app
COPY ./client/package*.json ./client/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY ./client .
RUN yarn build
ENV NODE_ENV production

FROM python:3.9
RUN mkdir /app
COPY ./requirements.txt /app

# Setting up the working directory
WORKDIR /app
RUN python3 -m pip install -r requirements.txt
RUN pip install --no-deps langflow==0.0.54
RUN pip install --no-deps chainfury

# Bundle app source
RUN rm -rf /app/static
RUN rm -rf /app/templates
COPY --from=builder /app/dist ./static
COPY --from=builder /app/dist/index.html ./templates/index.html

COPY ./server /app

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

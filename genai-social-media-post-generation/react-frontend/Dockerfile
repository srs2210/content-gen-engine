FROM node:21-alpine
RUN mkdir app
WORKDIR /app
COPY yarn.lock /app/yarn.lock
COPY package.json /app/package.json
RUN yarn install
COPY . /app
RUN yarn build
EXPOSE 3000
CMD ["yarn", "serve"]
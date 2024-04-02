FROM node:21.5-bullseye-slim
WORKDIR /app
COPY package*.json ./
COPY ./public ./public
COPY ./src ./src
COPY ./test ./test
COPY *.config.js ./
RUN npm install
ENV CHOKIDAR_USEPOLLING=true
EXPOSE 3000
CMD ["npm", "start"]

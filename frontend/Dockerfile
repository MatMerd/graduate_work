FROM node:18.12

WORKDIR /

EXPOSE 3000
COPY package.json ./
COPY package-lock.json ./

RUN npm install --no-audit && \
    npm cache clean --force

COPY . ./

CMD ["npm", "start"]
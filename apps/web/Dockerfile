FROM node:22-slim

WORKDIR /workspace

COPY package.json ./
COPY apps/web/package.json apps/web/package.json

RUN npm install

COPY apps ./apps

CMD ["npm", "run", "--workspace", "apps/web", "dev", "--", "--host", "0.0.0.0"]


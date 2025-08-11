FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm i --legacy-peer-deps || true
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm","start"]

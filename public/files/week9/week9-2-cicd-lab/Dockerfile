FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY app.js ./

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["npm", "start"]

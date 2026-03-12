FROM node:18-slim AS builder

WORKDIR /app

# Install dependencies
COPY autoapply/frontend/package*.json ./
RUN npm install

# Copy frontend code
COPY autoapply/frontend/ .

# Build the application
RUN npm run build

# Runner stage
FROM node:18-slim AS runner

WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]

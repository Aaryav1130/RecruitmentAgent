# ── Stage: React Frontend (Vite) ─────────────────────────────────────
FROM node:18-alpine

WORKDIR /app

# Copy dependency manifests for layer caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy all source code
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

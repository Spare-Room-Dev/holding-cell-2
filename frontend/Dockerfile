# Frontend Dockerfile for The Holding Cell
# Per D-03: Multi-stage build for Next.js static export served by nginx
# Static files generated during build, nginx serves them directly

# Stage 1: Builder - Build Next.js static export
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files for dependency installation
COPY package.json package-lock.json* ./

# Install dependencies (npm install works without lock file in workspace subdirectory)
RUN npm install

# Copy application source
COPY . .

# Build Next.js (creates /app/out directory with static files)
RUN npm run build

# Stage 2: Production - nginx serves static files
# Note: nginx.conf is mounted by docker-compose, not copied here
FROM nginx:alpine AS production

# Copy static files from builder stage
COPY --from=builder /app/out /usr/share/nginx/html

# Expose port 80 for nginx
EXPOSE 80

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
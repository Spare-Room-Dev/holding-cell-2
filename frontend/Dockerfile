# Frontend Dockerfile for The Holding Cell
# Per D-03: Multi-stage build for Next.js static export served by nginx
# Static files generated during build, nginx serves them directly

# Stage 1: Builder - Build Next.js static export
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files for dependency installation
COPY package.json package-lock.json* ./

# Install dependencies (npm ci for deterministic builds)
RUN npm ci

# Copy application source
COPY . .

# Build Next.js (creates /app/out directory with static files)
RUN npm run build

# Stage 2: Production - nginx serves static files
# Note: nginx.conf is mounted by docker-compose, not copied here
FROM nginx:alpine AS production

# Copy static files from builder stage
COPY --from=builder /app/out /usr/share/nginx/html

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port 80 for nginx
EXPOSE 80

# Start via entrypoint to copy files to volume
ENTRYPOINT ["/docker-entrypoint.sh"]
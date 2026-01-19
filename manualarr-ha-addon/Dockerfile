ARG BUILD_ARCH=amd64

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Final Image
# Use Debian base to ensure s6-overlay is present and avoid Alpine build issues
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base-debian:bookworm

# Install system dependencies including Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    libzbar0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

# Set up working directory
WORKDIR /app

# Install Python dependencies
# We use --break-system-packages because this is an isolated add-on container
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Link nginx logs to stdout/stderr for Home Assistant logging visibility
# And ensure nginx can write to its cache/log directories
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
    && chown -R www-data:www-data /var/lib/nginx /var/log/nginx

# Copy frontend build
COPY --from=frontend-build /app/dist /var/www/frontend

# Copy rootfs
COPY rootfs /

# Expose ingress port
EXPOSE 8080
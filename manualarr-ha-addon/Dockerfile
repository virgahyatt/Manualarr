ARG BUILD_ARCH=amd64

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Final Image
# We ignore BUILD_FROM to force the use of the Debian-based Python image
# which is required for building complex dependencies like pymupdf/pillow
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base-python:3.13

# Install system dependencies (Debian/apt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    libzbar0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Copy frontend build
COPY --from=frontend-build /app/dist /var/www/frontend

# Copy rootfs
COPY rootfs /

# Expose ingress port
EXPOSE 8080
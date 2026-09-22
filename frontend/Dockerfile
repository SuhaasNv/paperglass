# The Paperglass web app: a static build served by nginx, with /api proxied to the backend
# on the same origin so the session cookie needs no CORS.
#   docker build -t paperglass-frontend frontend/

FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
ARG PAPERGLASS_VERSION=dev
LABEL org.opencontainers.image.source="https://github.com/SuhaasNv/paperglass" \
      org.opencontainers.image.description="Paperglass web app" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="${PAPERGLASS_VERSION}"
# The official image renders /etc/nginx/templates/*.template with envsubst at start-up.
ENV PORT=8080 \
    BACKEND_URL=http://backend:8000
COPY docker/default.conf.template /etc/nginx/templates/default.conf.template
COPY docker/security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/" || exit 1

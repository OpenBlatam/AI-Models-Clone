# Etapa de build
FROM node:20-alpine AS builder
WORKDIR /app

# Copia todo el código fuente primero
COPY . .

# Instala dependencias
RUN if [ -f package-lock.json ]; then npm ci --legacy-peer-deps; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install; \
    elif [ -f yarn.lock ]; then yarn install; \
    else npm install --legacy-peer-deps; \
    fi

# Construye la aplicación
RUN npm run build

# Etapa de producción
FROM node:20-alpine AS runner
WORKDIR /app

COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/prisma ./prisma  # Asegúrate de copiar el esquema también si lo necesitas en runtime

EXPOSE 3000
CMD ["npm", "start"] 
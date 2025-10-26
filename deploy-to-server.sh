#!/bin/bash

# =============================================
# СКРИПТ ДЕПЛОЯ WEATHER APP НА ПРОДАКШЕН СЕРВЕР
# =============================================

# Цвета для красивого вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting deployment process...${NC}"

# ========================
# ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ========================

# Проверяем что переменные окружения установлены
if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${RED}❌ ERROR: DOCKER_USERNAME is not set${NC}"
    echo "Please set environment variable: export DOCKER_USERNAME=your_username"
    exit 1
fi

if [ -z "$OPENWEATHER_API_KEY" ]; then
    echo -e "${RED}❌ ERROR: OPENWEATHER_API_KEY is not set${NC}"
    echo "Please set environment variable: export OPENWEATHER_API_KEY=your_api_key"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables check passed${NC}"
echo -e "Docker Username: $DOCKER_USERNAME"
echo -e "API Key: ${OPENWEATHER_API_KEY:0:10}..." # Показываем только начало API ключа

# ========================
# ПОЛУЧЕНИЕ ОБРАЗОВ ИЗ DOCKER HUB
# ========================

echo -e "${YELLOW}📥 Pulling latest Docker images from Docker Hub...${NC}"

# Получаем последние версии образов с Docker Hub
docker pull $DOCKER_USERNAME/auth-backend:latest
docker pull $DOCKER_USERNAME/weather-backend:latest
docker pull $DOCKER_USERNAME/auth-frontend:latest
docker pull $DOCKER_USERNAME/weather-frontend:latest

echo -e "${GREEN}✅ All images successfully pulled${NC}"

# ========================
# ОСТАНОВКА СТАРЫХ КОНТЕЙНЕРОВ
# ========================

echo -e "${YELLOW}🛑 Stopping and removing old containers...${NC}"

# Останавливаем и удаляем старые контейнеры
docker-compose -f docker-compose.prod.yml down

echo -e "${GREEN}✅ Old containers stopped and removed${NC}"

# ========================
# ЗАПУСК НОВЫХ КОНТЕЙНЕРОВ
# ========================

echo -e "${YELLOW}🐳 Starting new containers with latest images...${NC}"

# Запускаем новые контейнеры с обновленными образами
DOCKER_USERNAME=$DOCKER_USERNAME OPENWEATHER_API_KEY=$OPENWEATHER_API_KEY \
docker-compose -f docker-compose.prod.yml up -d

echo -e "${GREEN}✅ New containers started successfully${NC}"

# ========================
# ОЖИДАНИЕ ЗАПУСКА СЕРВИСОВ
# ========================

echo -e "${YELLOW}⏳ Waiting for services to start (30 seconds)...${NC}"
sleep 30  # Даем время всем сервисам полностью запуститься

# ========================
# ПРОВЕРКА ЗДОРОВЬЯ СЕРВИСОВ
# ========================

echo -e "${YELLOW}🔍 Performing health checks...${NC}"

# Счетчики для проверки
SUCCESS_COUNT=0
TOTAL_SERVICES=4

# Проверка фронтенда авторизации (порт 3001)
if curl -f http://localhost:3001/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Auth Frontend (port 3001) is responding${NC}"
    ((SUCCESS_COUNT++))
else
    echo -e "${RED}❌ Auth Frontend (port 3001) is not responding${NC}"
fi

# Проверка фронтенда погоды (порт 3000)
if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Weather Frontend (port 3000) is responding${NC}"
    ((SUCCESS_COUNT++))
else
    echo -e "${RED}❌ Weather Frontend (port 3000) is not responding${NC}"
fi

# Проверка бэкенда авторизации (порт 8081)
if curl -f http://localhost:8081/api/auth/test > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Auth Backend (port 8081) is responding${NC}"
    ((SUCCESS_COUNT++))
else
    echo -e "${RED}❌ Auth Backend (port 8081) is not responding${NC}"
fi

# Проверка бэкенда погоды (порт 8080)
if curl -f http://localhost:8080/api/weather/test > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Weather Backend (port 8080) is responding${NC}"
    ((SUCCESS_COUNT++))
else
    echo -e "${RED}❌ Weather Backend (port 8080) is not responding${NC}"
fi

# ========================
# ФИНАЛЬНЫЙ ОТЧЕТ
# ========================

echo -e "${YELLOW}📊 Deployment Summary:${NC}"
echo -e "   Services healthy: $SUCCESS_COUNT/$TOTAL_SERVICES"

if [ $SUCCESS_COUNT -eq $TOTAL_SERVICES ]; then
    echo -e "${GREEN}🎉 All services are healthy! Deployment completed successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may need attention. Check logs with: docker-compose logs${NC}"
fi

echo -e "${YELLOW}🌐 Application URLs:${NC}"
echo -e "   🌤️  Weather Frontend: http://your-server.com:3000 (or your domain)"
echo -e "   🔐 Auth Frontend:    http://your-server.com:3001"
echo -e "   ⚙️  Auth Backend:     http://your-server.com:8081"
echo -e "   🌤️  Weather Backend:  http://your-server.com:8080"

echo -e "${YELLOW}📈 Container status:${NC}"
docker-compose -f docker-compose.prod.yml ps

# ========================
# ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ ДЛЯ АДМИНИСТРИРОВАНИЯ
# ========================

echo -e "${YELLOW}🛠️  Useful commands:${NC}"
echo -e "   View logs:              docker-compose logs"
echo -e "   View specific service:  docker-compose logs auth-backend"
echo -e "   Restart service:        docker-compose restart auth-backend"
echo -e "   Stop all services:      docker-compose down"
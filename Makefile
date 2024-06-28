# Команды Docker Compose
DC=docker compose

# Файлы Docker Compose
COMPOSE_FILES=-f docker-compose.yml

# Цели
.PHONY: up down restart logs build pull ps exec clean pull-restart

# Поднятие всех сервисов
up:
	$(DC) $(COMPOSE_FILES) up -d

# Остановка всех сервисов
down:
	$(DC) $(COMPOSE_FILES) down

stop:
	$(DC) $(COMPOSE_FILES) stop

# Перезапуск всех сервисов
restart: down up

# Просмотр логов всех сервисов
logs:
	$(DC) $(COMPOSE_FILES) logs -f

# Сборка всех сервисов
build:
	$(DC) $(COMPOSE_FILES) build

# Обновление образов для всех сервисов
pull:
	$(DC) $(COMPOSE_FILES) pull

# Просмотр состояния всех сервисов
ps:
	$(DC) $(COMPOSE_FILES) ps

# Выполнение команды в контейнере
exec:
	$(DC) $(COMPOSE_FILES) exec $(SERVICE) $(COMMAND)

# Очистка неиспользуемых данных Docker
clean:
	docker system prune -f

# Обновление репозитория и перезапуск сервисов
pull-restart: git-pull down stop up

# Выполнение git pull
git-pull:
	git pull

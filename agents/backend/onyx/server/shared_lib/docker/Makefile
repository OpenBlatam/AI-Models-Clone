# Makefile para Docker Operations
# =================================

.PHONY: help build build-dev build-alpine build-serverless run stop clean logs test push

# Variables
IMAGE_NAME = shared-lib
VERSION = latest
PORT = 8030

help:
	@echo "Docker Operations for Shared Library"
	@echo ""
	@echo "Commands:"
	@echo "  make build          - Build production image"
	@echo "  make build-dev      - Build development image"
	@echo "  make build-alpine    - Build Alpine-based image"
	@echo "  make build-serverless - Build serverless image"
	@echo "  make run             - Run container"
	@echo "  make stop            - Stop container"
	@echo "  make clean           - Remove containers and images"
	@echo "  make logs            - Show container logs"
	@echo "  make test            - Run tests in container"
	@echo "  make push            - Push image to registry"
	@echo "  make compose-up      - Start with docker-compose"
	@echo "  make compose-down    - Stop docker-compose"

build:
	docker build -f docker/Dockerfile -t $(IMAGE_NAME):$(VERSION) ..

build-dev:
	docker build -f docker/Dockerfile.dev -t $(IMAGE_NAME):dev ..

build-alpine:
	docker build -f docker/Dockerfile.alpine -t $(IMAGE_NAME):alpine ..

build-serverless:
	docker build -f docker/Dockerfile.serverless -t $(IMAGE_NAME):serverless ..

run:
	docker run -d --name $(IMAGE_NAME)-container -p $(PORT):8030 $(IMAGE_NAME):$(VERSION)

stop:
	docker stop $(IMAGE_NAME)-container || true
	docker rm $(IMAGE_NAME)-container || true

clean:
	docker stop $(IMAGE_NAME)-container || true
	docker rm $(IMAGE_NAME)-container || true
	docker rmi $(IMAGE_NAME):$(VERSION) || true

logs:
	docker logs -f $(IMAGE_NAME)-container

test:
	docker run --rm $(IMAGE_NAME):$(VERSION) pytest

push:
	docker push $(IMAGE_NAME):$(VERSION)

compose-up:
	cd docker && docker-compose up -d

compose-down:
	cd docker && docker-compose down

compose-prod:
	cd docker && docker-compose -f docker-compose.prod.yml up -d





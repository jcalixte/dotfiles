COMPOSE ?= docker compose

.PHONY: up down logs smoke shell reset

up:          ## Start CouchDB and wait for it
	$(COMPOSE) up -d --build
	$(COMPOSE) ps

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f couchdb

smoke:       ## Verify the instance end to end
	bash scripts/smoke.sh

shell:
	$(COMPOSE) exec couchdb bash

reset:       ## Destroy the data volume and start clean
	$(COMPOSE) down -v
	$(COMPOSE) up -d --build

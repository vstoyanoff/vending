SHELL := /bin/bash -e -o pipefail

.PHONY : production
production:
	docker-compose up -d

.PHONY : develop
develop:
	docker-compose -f docker-compose.dev.yml up -d --build
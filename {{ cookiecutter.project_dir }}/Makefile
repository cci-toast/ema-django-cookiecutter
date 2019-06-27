.PHONY: shell test rebuild

rebuild:
	@echo "Rebuilding local docker-compose images..."
	docker-compose kill
	docker-compose rm -f web
	docker-compose build --force-rm web

shell:
	docker-compose run --rm web bash

test:
	docker-compose run --rm web pytest

isort:
	isort -rc --atomic .

black:
	black .

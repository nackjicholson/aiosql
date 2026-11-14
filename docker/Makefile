SHELL   = /bin/bash
.ONESHELL:

DOCKER	= docker
NAME	= aiosql-tests

clean:
	TEST=pytest $(DOCKER) compose down -v
	$(RM) .docker-aiosql-*

#
# Build docker client images
#
# NOTE it really depends on the base image version and
# when it is run to know which are the latest packages
# --no-cache? docker build prune?
CACHE   =
# CACHE	= --no-cache

.docker-aiosql-%: container.%
	tag=$@
	tag=python-aiosql-$${tag#.docker-aiosql-}
	$(DOCKER) build $(CACHE) -t $$tag -f $< . && touch $@

.PHONY: docker.aiosql
docker.aiosql: \
	.docker-aiosql-pg \
	.docker-aiosql-mysql \
	.docker-aiosql-dbs

#
# Run tests with docker
#
.PHONY: docker.run
docker.run: docker.run.pg docker.run.mysql docker.run.dbs

foo:
	echo "# starting up…"
	$(DOCKER) compose up -d
	# wait and show results, in probable completion order
	# $(DOCKER) container logs -f $(NAME)-dbs-client-1
	$(DOCKER) container wait $(NAME)-dbs-client-1
	$(DOCKER) container logs $(NAME)-dbs-client-1
	# $(DOCKER) container logs -f $(NAME)-my-client-1
	$(DOCKER) container wait $(NAME)-my-client-1
	$(DOCKER) container logs $(NAME)-my-client-1
	# $(DOCKER) container logs -f $(NAME)-pg-client-1
	echo "# shutting down…"
	$(DOCKER) compose down -v

.PHONY: check.test
check.test:
	[ "$$TEST" ] || { echo "# Missing \$$TEST" >&2 ; exit 1 ; }
	[ "$$TEST" = "pytest" -o "$$TEST" = "coverage" ] || { echo "# Bad \$$TEST: $$TEST" ; exit 2 ; }

.PHONY: docker.run.%
docker.run.%: check.test
	DB=$@
	DB=$${DB#docker.run.}
	echo "# DB=$$DB TEST=$$TEST"
	$(DOCKER) compose -f docker-compose.$$DB.yml up -d
	$(DOCKER) container wait $(NAME)-$$DB-client-1
	$(DOCKER) container logs $(NAME)-$$DB-client-1
	$(DOCKER) compose -f docker-compose.$$DB.yml down -v

.PHONY: docker.pytest
docker.pytest:
	export TEST=pytest
	$(MAKE) docker.run

.PHONY: docker.coverage
docker.coverage:
	export TEST=coverage
	$(MAKE) docker.run

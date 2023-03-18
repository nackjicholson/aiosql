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
CACHE	= --no-cache

.docker-aiosql-%: dockerfile.python-%
	tag=$@
	tag=$${tag#.docker-aiosql-}
	tag=python-aiosql-$$tag
	$(DOCKER) build $(CACHE) -t $$tag -f $< . && touch $@

.PHONY: docker.aiosql
docker.aiosql: \
	.docker-aiosql-postgres \
	.docker-aiosql-mysql \
	.docker-aiosql-mariadb

#
# Run tests with docker
#
.PHONY: docker.run
docker.run:
	[ "$$TEST" ] || { echo "# Missing \$$TEST" >&2 ; exit 1 ; }
	echo "# starting up…"
	$(DOCKER) compose up -d
	# wait and show results, in probable completion order
	# $(DOCKER) container logs -f $(NAME)-ma-client-1
	$(DOCKER) container wait $(NAME)-ma-client-1
	$(DOCKER) container logs $(NAME)-ma-client-1
	# $(DOCKER) container logs -f $(NAME)-my-client-1
	$(DOCKER) container wait $(NAME)-my-client-1
	$(DOCKER) container logs $(NAME)-my-client-1
	# $(DOCKER) container logs -f $(NAME)-pg-client-1
	$(DOCKER) container wait $(NAME)-pg-client-1
	$(DOCKER) container logs $(NAME)-pg-client-1
	echo "# shutting down…"
	$(DOCKER) compose down -v

.PHONY: docker.pytest
docker.pytest:
	export TEST=pytest
	$(MAKE) docker.run

.PHONY: docker.coverage
docker.coverage:
	export TEST=coverage
	$(MAKE) docker.run

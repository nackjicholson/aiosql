.ONESHELL:

DOCKER	= docker
NAME	= aiosql-pytest

clean:
	TEST=pytest $(DOCKER) compose down -v
	$(RM) .aiosql-python-*

# build client images
.aiosql-python-%: dockerfile.python-%
	tag=$@
	tag=$${tag#.}
	$(DOCKER) build -t $$tag -f $< .
	touch $@

.PHONY: aiosql-python
aiosql-python: \
	.aiosql-python-postgres \
	.aiosql-python-mysql \
	.aiosql-python-mariadb

.PHONY: run
run:
	echo "# starting up…"
	$(DOCKER) compose up -d
	# wait and show results, in probable completion order
	# $(DOCKER) container logs -f $(NAME)-ma-client-1
	$(DOCKER) container wait $(NAME)-ma-client-1
	$(DOCKER) container logs $(NAME)-ma-client-1
	# $(DOCKER) container logs -f $(NAME)-pg-client-1
	$(DOCKER) container wait $(NAME)-pg-client-1
	$(DOCKER) container logs $(NAME)-pg-client-1
	# $(DOCKER) container logs -f $(NAME)-my-client-1
	$(DOCKER) container wait $(NAME)-my-client-1
	$(DOCKER) container logs $(NAME)-my-client-1
	echo "# shutting down…"
	$(DOCKER) compose down -v

.PHONY: docker.pytest
docker.pytest:
	export TEST=pytest
	$(MAKE) run

.PHONY: docker.coverage
docker.coverage:
	export TEST=coverage
	$(MAKE) run

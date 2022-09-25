.ONESHELL:

DOCKER	= docker

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
	$(DOCKER) compose -p aiosql up -d
	# $(DOCKER) container logs -f aiosql-ma-client-1
	$(DOCKER) container wait aiosql-ma-client-1
	$(DOCKER) container logs aiosql-ma-client-1
	# $(DOCKER) container logs -f aiosql-my-client-1
	$(DOCKER) container wait aiosql-my-client-1
	$(DOCKER) container logs aiosql-my-client-1
	# $(DOCKER) container logs -f aiosql-pg-client-1
	$(DOCKER) container wait aiosql-pg-client-1
	$(DOCKER) container logs aiosql-pg-client-1
	echo "# shutting down…"
	$(DOCKER) compose -p aiosql down -v

docker.pytest:
	export TEST=pytest
	$(MAKE) run

docker.coverage:
	export TEST=coverage
	$(MAKE) run

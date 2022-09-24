.ONESHELL:

DOCKER	= docker

clean:
	$(RM) .aiosql-python-*

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

docker.pytest:
	export TEST=pytest
	$(DOCKER) compose -p aiosql up

docker.coverage:
	export TEST=coverage
	$(DOCKER) compose -p aiosql up

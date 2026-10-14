include prelude.mk

.PHONY: all
all:

.PHONY: test
test:
	./test/runner/harness

test/docker/%: DO
	cd test/docker && \
		DISTRO='$*' docker compose build --force-rm -q && \
		docker compose run --rm test && \
		docker compose down -v

# Keep the list distros synced with the GitHub actions workflow.
.PHONY: test/docker
test/docker: test/docker/noble
test/docker: test/docker/resolute

##@ Run

##@ Test
test:
	uv run pyright
	uv run python -m unittest
	

##@ Clean
.PHONY: clean
clean: ## Clean up generated files.
	rm -f .venv

define env_content
PRDRAFT_GITHUB_TOKEN=${PRDRAFT_GITHUB_TOKEN}
endef

export env_content
.env: ## Write .env file. Required environment variables: PRDRAFT_GITHUB_TOKEN
	echo "$$env_content" > .env

.venv/bin/prdraft:
	uv sync

##@ Help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[.a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.DEFAULT_GOAL = help

.PHONY: test help


pr_file ?= dataset/pr.jsonl

##@ Run
$(pr_file): .env .venv/bin/onagigawa ## Fetch pull requests.
	mkdir -p $(shell dirname $(pr_file))
	uv run  --env-file=.env onagigawa --verbose pr alpdr data-platform $(pr_file)


##@ Clean
.PHONY: clean
clean: ## Clean up generated files.
	rm -f .venv

define env_content
ONAGIGAWA_GITHUB_API_KEY=$(ONAGIGAWA_GITHUB_API_KEY)
endef

export env_content
.env: ## Write .env file. Required environment variables: ONAGIGAWA_GITHUB_API_KEY
	echo "$$env_content" > .env

.venv/bin/onagigawa:
	uv sync

##@ Help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[.a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.DEFAULT_GOAL = help

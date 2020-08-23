# Set shell
SHELL=/bin/bash -e -o pipefail


# This Makefile allows to trigger the CI and CD pipelines, as well as individual steps

# ----------------------------------------------------
#
# CI/CD Pipeline
#
# ----------------------------------------------------
.PHONY: run-ci-pipeline run-cd-pipeline run-ci-cd-pipeline

run-ci-cd-pipeline: run-ci-pipeline run-cd-pipeline

run-ci-pipeline:
	@ ./build_steps/run_ci_pipeline.sh

run-cd-pipeline:
	@ ./build_steps/run_cd_pipeline.sh


# ----------------------------------------------------
#
# CI STEPS
#
# ----------------------------------------------------
.PHONY: env pre-commit lint recreatedb

env:
	@ ./build_steps/ci_pipeline/1_set_environment.sh
	@ INFO "Please activate the conda environment and source your environment variables:"
	@ MESSAGE "- conda activate ${CONDA_ENV_NAME}"
	@ MESSAGE "- source .env"

pre-commit:
	@ pre-commit install -t pre-commit -t commit-msg
	@ SUCCESS "pre-commit set up successfully!"

lint: 
	@ ./build_steps/ci_pipeline/2_lint_code.sh

tests:
	@ ./build_steps/ci_pipeline/3_run_pytest.sh

build:
	@ docker build -t ${IMAGE_REPOSITORY} .

up:
	@ cd deployment && docker-compose up -d

down:
	@ cd deployment && docker-compose down
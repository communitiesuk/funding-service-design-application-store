# Funding service design application store.

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[![Deploy to Gov PaaS](https://github.com/communitiesuk/funding-service-design-application-store/actions/workflows/deploy.yml/badge.svg)](https://github.com/communitiesuk/funding-service-design-application-store/actions/workflows/deploy.yml)

[![CodeQL](https://github.com/communitiesuk/funding-service-design-application-store/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/communitiesuk/funding-service-design-application-store/actions/workflows/codeql-analysis.yml)

This is a Flask API that provides access to the Funding Service Design Application Store. The frontend repository for
this data store is [here](https://github.com/communitiesuk/funding-service-design-frontend).

## Prerequisites

- python ^= 3.10

# Getting started

## Installation

Clone the repository

### Create a Virtual environment

    python3 -m venv .venv

### Enter the virtual environment

...either macOS using bash:

    source .venv/bin/activate

...or if on Windows using Command Prompt:

    .venv\Scripts\activate.bat

### Install dependencies

requirements-dev.txt and requirements.txt are updated using [pip-tools pip-compile](https://github.com/jazzband/pip-tools)
To update requirements please manually add the dependencies in the .in files (not the requirements.txt files)
Then run (in the following order):

    pip-compile requirements.in

    pip-compile requirements-dev.in

From the top-level directory enter the command to install pip and the dependencies of the project

    python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt

## How to use

Enter the virtual environment as described above, then run:

    flask run

A local dev server will be created on

    http://127.0.0.1:5000/

This is configurable in .flaskenv

# Pipelines

* Deploy to Gov PaaS - This is a simple pipeline to demonstrate capabilities. Builds, tests and deploys a simple python
  application to the PaaS for evaluation in Dev and Test Only.

# Testing

To run all unit tests run 'pytest'

## Performance Testing

Performance tests are stored in a separate repository which is then run in the pipeline. If you want to run the
performance tests yourself follow the steps in the README for the performance test repo
located [here](https://github.com/communitiesuk/funding-service-design-performance-tests/blob/main/README.md)

# Extras

This repo comes with a .pre-commit-config.yaml, if you wish to use this do the following while in your virtual
enviroment:

    pip install pre-commit black

    pre-commit install

Once the above is done you will have autoformatting and pep8 compliance built into your workflow. You will be notified
of any pep8 errors during commits.

In deploy.yml, there are three environment variables called users, spawn-rate and run-time. These are used
to override the locust config if the performance tests need to run with different configs for application store.

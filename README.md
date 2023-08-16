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

### Postgres

You will need to set up a local postgres server to run and test this repo.

Set the environment variables "DATABASE_URL" to your postgres connection string before running `flask` or `pytest`.

Eg.

`export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres`


### Build with Paketo

[Pack](https://buildpacks.io/docs/tools/pack/cli/pack_build/)

[Paketo buildpacks](https://paketo.io/)

```pack build <name your image> --builder paketobuildpacks/builder:base```

Example:

```
[~/work/repos/funding-service-design-application-store] pack build paketo-demofsd-app --builder paketobuildpacks/builder:base
***
Successfully built image paketo-demofsd-app
```

You can then use that image with docker to run a container

```
docker run -d -p 8080:8080 --env PORT=8080 --env FLASK_ENV=dev [envs] paketo-demofsd-app
```

`envs` needs to include values for each of:
NOTIFICATION_SERVICE_HOST
ACCOUNT_STORE_API_HOST
FUND_STORE_API_HOST
SENTRY_DSN
GITHUB_SHA
DATABASE_URL

```
docker ps -a
CONTAINER ID   IMAGE                       COMMAND                  CREATED          STATUS                    PORTS                    NAMES
42633142c619   paketo-demofsd-app          "/cnb/process/web"       8 seconds ago    Up 7 seconds              0.0.0.0:8080->8080/tcp   peaceful_knuth
```


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

# Scripts
## send_applications_on_closure
Sends the contents of all unsubmitted applications in a particular round to the applicant for their records.

### Execution

#### PaaS

Execute the script as a task (example is for COF R2W3)
`cf run-task funding-service-design-application-store-dev --command "./scripts/send_application_on_closure.py --fund_id=47aef2f5-3fcb-4d45-acb5-f0152b5f03c4 --round_id=5cf439bf-ef6f-431e-92c5-a1d90a4dd32f --send_emails=True" --name unsubmitted_emails`

View logs
`cf logs funding-service-design-application-store-dev --recent | grep unsubmitted_emails`

#### Local
Run the full service via the docker runner, then find the container ID of the application-store:
`docker ps`
Then copy that container id and execute as below:
`funding-service-design-application-store % docker exec -it <app-store container id> scripts/send_application_on_closure.py --fund_id=47aef2f5-3fcb-4d45-acb5-f0152b5f03c4 --round_id=5cf439bf-ef6f-431e-92c5-a1d90a4dd32f --send_emails=True`

### Useful Queries
Show count of applications by status for each round
`select fund_id, round_id, status, count(status) from applications group by fund_id, status, round_id;`
Total to be sent, by fund/round
`select fund_id, round_id, count(id) from applications where status not in ('SUBMITTED') group by fund_id, round_id;`

## Copilot Initialisation

Copilot is the deployment of the infrastructure configuration, which is all stored under the copilot folder. The manifest files have been pre-generated by running through various initialisation steps that create the manifest files by prompting a series of questions, but do not _deploy_ the infrastructure.

For each AWS account, these commands will need to be run _once_ to initialise the environment:

`copilot app init pre-award` - this links the pre-award app with the current service, and associates the next commands with the service. Essentially, this provides context for the service to run under

```
copilot init \
    --name fsd-application-store \
    --app pre-award \
    --type 'Backend Service' \
    --image 'ghcr.io/communitiesuk/funding-service-design-application-store:latest' \
    --port 80
```

This will initalise this service, using the current created image


# Seeding Test Data
You can seed test data to use in the running application (separate to unit test data seeding). The seeding process needs a running fund-store to retrieve fund/round form section config, so it runs within the docker container for application-store within the docker runner.
To run the seeding script:
1. Make sure your local docker-runner is running
1. Find the container ID of `application-store` by using `docker ps`
1. Use docker exec to get into that container: `docker exec -it <container_id> bash`
1. Execute the script: `python scripts/seed_db_test_data.py`. You will be prompted for inputs: fund, round, account_id (the UUID not email address), the status of the seeded applications and how many to create.

## Testing the seeding process
Unit tests exist in [test_seed_db](/tests/test_seed_db.py). They are marked as skipped as they require a running fund-store to retrieve form config (no point in duplicating this for tests) so they won't run in the pipeline but are fine locally. If your local fund store runs on a non-standard port etc, edit the `local_fund_store` fixture in that tests file. If you want to run the tests, just comment out the skip marker.

## Adding a new fund/round to the seeding process
To seed applicaitons, we need the completed form json. If you have that, skip to the end of part 1 and put that form json into the required file.

### Part 1 - get the form json
1. Get a submitted application into your local DB. You can either do this manually or by running the automated tests against your local docker runner.
1. Find the `application_id` of that submitted application._
1. Edit the [tests file](/tests/test_seed_db.py) to un-skip `test_retrieve_test_data` and then set `target_app` to be the `application_id` you just submitted.
1. Update your unit test config to point at the same DB as the docker runner. Update [pytest.ini](/pytest.ini) so that `D:DATABASE_URL` points at the docker runner application store db: `D:DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/application_store`
1. Run the single test `test_retrieve_test_data` - this should output the json of all the completed forms for that application into funding-service-design-store/forms.json.
1. Copy this file into [seed_data](/tests/seed_data/) and name it `<fund_short_code>_<round_short_code>_all_forms.json`.
1. *IMPORTANT* Change the config in [pytest.ini](/pytest.ini) back to what it was so you don't accidentally wipe your docker runner DB next time you run tests!

### Part 2 - update seeding config
1. In [seed_db](/tests/seed_data/seed_db.py) there is a constant called `FUND_CONFIG` - update this following the existing structure for your new fund/round (if it's a new round on an existing fund, just add it as another key to `rounds` item in that fund). You will need to know the name of the form that contains the field used to the name the application/project.
1. In the same file, update the `click.option` choice values for fund/round as required, to allow your new options.
1. Test it - update the unit tests to use this new config and check it works.

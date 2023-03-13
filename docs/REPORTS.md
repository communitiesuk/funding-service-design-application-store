#### This README describes three endpoints related to reporting on applications in a funding service. All endpoints are part of the /applications/reporting path.


## Running on local environment

The easiest way to run these requests on your local environment is to use the default open api web interface. To do this, run the application locally and navigate to http://localhost:3002/. You can then use the interface to run the requests and download the CSV files.

## Running on external environments

1. GET /applications/reporting/applications_statuses_data:

This endpoint returns a CSV report on the status of started and submitted applications. It accepts two optional query parameters: round_id and fund_id, which can be used to filter the report by round and fund IDs, respectively. If no query parameters are provided, the endpoint will return the report for all applications.

To get the report using the command line, use the following command:

```bash
cf ssh funding-service-design-application-store --command "curl --silent localhost:8080/applications/reporting/applications_statuses_data" > output.csv
```

2. GET /applications/reporting/key_application_metrics

This endpoint returns a CSV report on key data related to applications. It accepts three optional query parameters: status, round_id, and fund_id, which can be used to filter the report by application status, round ID, and fund ID, respectively. If no query parameters are provided, the endpoint will return the report for all applications.

To get the report using the command line, use the following command:

```bash
cf ssh funding-service-design-application-store --command "curl --silent localhost:8080/applications/reporting/key_application_metrics" > output.csv
```

3. GET /applications/reporting/key_application_metrics/{application_id}

This endpoint returns a CSV report on key data related to a specific application identified by application_id. No query parameters are accepted.

To get the report using the command line, use the following command:

```bash
cf ssh funding-service-design-application-store --command "curl --silent localhost:8080/applications/reporting/key_application_metrics/<application_id>" > output.csv
```

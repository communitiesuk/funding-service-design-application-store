# Scripts
## send_applications_on_closure
- Sends the contents of all unsubmitted applications in a particular round to the applicant for their records.
- Sends the contents of single unsubmitted application in a particular round to the applicant for their records
if --single_application is set to True.

  ### Run locally
  - Example without --single_application and application_id

    `python -m scripts.send_application_on_closure --fund_id 47aef2f5-3fcb-4d45-acb5-f0152b5f03c4 --round_id e85ad42f-73f5-4e1b-a1eb-6bc5d7f3d762 --send_email False`

  - Example with --single_application and application_id

    `python -m scripts.send_application_on_closure --fund_id 47aef2f5-3fcb-4d45-acb5-f0152b5f03c4 --round_id e85ad42f-73f5-4e1b-a1eb-6bc5d7f3d762 --single_application True --application_id 2ad3c0e5-ad9b-4dfb-ab95-95a758f73cba --send_email False`

   ### Run with docker
   - Example without --single_application and application_id

     `docker exec -ti $(docker ps -qf "name=application-store") scripts/send_application_on_closure.py --fund_id 47aef2f5-3fcb-4d45-acb5-f0152b5f03c4 --round_id 6af19a5e-9cae-4f00-9194-cf10d2d7c8a7 --send_email False`

   - Example with --single_application and application_id

     `docker exec -ti $(docker ps -qf "name=application-store") scripts/send_application_on_closure.py --fund_id 47aef2f5-3fcb-4d45-acb5-f0152b5f03c4 --round_id 6af19a5e-9cae-4f00-9194-cf10d2d7c8a7  --single_application True --application_id  ea9878ec-6d5b-483e-b50b-91f518695743 --send_email False`

   ### Run on cf

   - Example without --single_application and application_id

      `cf run-task funding-service-design-application-store-test --command "python -m scripts.send_application_on_closure --fund_id 47aef2f5-3fcb-4d45-acb5-f0152b5f03c4 --round_id 6af19a5e-9cae-4f00-9194-cf10d2d7c8a7 --send_email False`

    - Example with --single_application and application_id

      `cf run-task funding-service-design-application-store-test --command "python -m scripts.send_application_on_closure --fund_id 47aef2f5-3fcb-4d45-acb5-f0152b5f03c4 --round_id 6af19a5e-9cae-4f00-9194-cf10d2d7c8a7 --single_application True --application_id 2ad3c0e5-ad9b-4dfb-ab95-95a758f73cba --send_email False`

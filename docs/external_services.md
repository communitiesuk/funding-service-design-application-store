#### This README describes the exteranl service that the application store interacts with

## [Fund store](https://github.com/communitiesuk/funding-service-design-fund-store)

## [Application Frontend](https://github.com/communitiesuk/funding-service-design-frontend)

## [Form runner](https://github.com/communitiesuk/funding-service-design-docker-runner)

## Amazon Simple Queue Service
As part of the application submission workflow, we use a [FIFO AWS SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html) to automate our application export to assessment.

We export the application as a 'fat' payload. This includes all application data (including metadata/attributes), this ensure assessment does not need to call application_store for additional information. 

We can simulate an SQS locally when using our docker runner instance. Our docker runner uses localstack to simulate these  AWS services, see [here](https://github.com/communitiesuk/funding-service-design-docker-runner/tree/main/docker-localstack). 

If messages are not consumed and deleted they will be move to the Dead-Letter_Queue, here we can inspect the message for faults and retry.

The SQS queues have a number of confiuration options, we are using the AWS SDK for Python (Boto3), see docs [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html). 

There is an API endpoint on this service to send a submitted application to assessment: 
    
    ```
    /queue/{queue_name}/{application_id}
    ```
    
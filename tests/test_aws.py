import pytest
from external_services.aws import list_files_by_prefix


# You can use this for testing the function if doing tdd.
# I will write some proper unit tests later when I have time.
@pytest.mark.skip()
def test_list_files_recursive():
    bucket_name = (  # this is form-uploads-dev
        "paas-s3-broker-prod-lon-443b9fc2-55ff-4c2f-9ac3-d3ebfb18ef5a"
    )
    prefix = (  # this was just a mock application id i used for testing.
        "my-application-id/"
    )

    files = list_files_by_prefix(bucket_name, prefix)
    assert len(files) != 0

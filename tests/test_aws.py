import pytest
from external_services.aws import list_files_by_prefix


# You can use this for testing the function if doing tdd.
@pytest.mark.skip()
def test_list_files_tdd():
    bucket_name = (  # this is form-uploads-dev
        "paas-s3-broker-prod-lon-443b9fc2-55ff-4c2f-9ac3-d3ebfb18ef5a"
    )
    prefix = (  # this was just a mock application id I used for testing.
        "my-application-id/"
    )

    files = list_files_by_prefix(bucket_name, prefix)
    assert len(files) != 0


def test_list_files_by_prefix_multiple_files(mocker):
    """
    GIVEN an S3 objects response with multiple files
    WHEN calling list_files_by_prefix with a prefix
    THEN it should return a list of FileData instances with the correct key parts
    """
    prefix = "application_id/"
    objects_response = {
        "Contents": [
            {"Key": f"{prefix}form/path/component_id/filename1"},
            {"Key": f"{prefix}form/path/component_id/filename2"},
            {
                "Key": f"{prefix}wrong_path_somehow/filename2"
            },  # ignored, not enough key parts (this won't happen)
        ]
    }
    mocker.patch(
        "external_services.aws._S3_CLIENT.list_objects_v2",
        return_value=objects_response,
    )

    result = list_files_by_prefix(prefix)
    assert len(result) == 2

    file1, file2 = result
    assert file1.application_id == file2.application_id == "application_id"
    assert file1.component_id == file2.component_id == "component_id"
    assert file1.form == file2.form == "form"
    assert file1.path == file2.path == "path"

    assert file1.filename == "filename1"
    assert file2.filename == "filename2"

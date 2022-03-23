from tests.helpers import expected_data_within_get_response
from tests.helpers import expected_data_within_put_response


def test_get_status_response(flask_test_client):
    """_summary_: Function send an application id as
    a key with endpoint & returns expected output

    Args:
        flask_test_client
    """

    expected_data = {
        "Application id": "uuidv4",
        "Questions": {"Q1": "NOT STARTED"},
    }

    expected_data_within_get_response(
        flask_test_client, "/fund/status/uuidv4", expected_data, debug=True
    )


def test_update_status_response(flask_test_client):
    """_summary_: Function send an application id as
    a key with endpoint & returns expected output

    Args:
        flask_test_client
    """

    expected_data = {"Q1": "COMPLETED"}

    expected_data_within_put_response(
        flask_test_client, "/fund/status/uuidv4/Q1", expected_data, debug=True
    )

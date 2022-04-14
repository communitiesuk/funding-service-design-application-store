import time

from tests.helpers import count_fund_applications
from tests.helpers import expected_data_within_get_response
from tests.helpers import post_data


# TODO: Not possible to test all applications currently as unpredictable UID in default data
# def test_search_endpoint_get_all_applications(flask_test_client):
#     """
#     GIVEN We have a functioning Application Store API
#     WHEN a request for applications with no set params
#     THEN the response should return all applications
#     """
#     expected_data = [
#         {
#             "id": "uuidv4",
#             "status": "COMPLETED",
#             "assessment_deadline": "2022-08-28 00:00:00",
#             "fund_id": "slugified_test_fund_name"
#         },
#         {
#             "id": "uuidv4-2",
#             "status": "NOT_STARTED",
#             "assessment_deadline": "2022-08-28 00:00:00",
#             "fund_id": "slugified_test_fund_name"
#         }
#     ]
#
#     exclude_regex_paths = r"root\[\d+\]\['id'\]"
#     expected_data_within_get_response(
#         flask_test_client,
#         "/applications",
#         expected_data,
#         exclude_regex_paths=exclude_regex_paths
#     )


def test_get_applications_by_status_completed(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications with a given status
    THEN the response should only contain the applications that
    have that status
    """
    expected_data = [
        {
            "id": "uuidv4",
            "status": "COMPLETED",
            "fund_id": "test-fund-name",
            "round_id": "spring",
            "date_submitted": "2021-12-24 00:00:00",
            "assessment_deadline": "2022-08-28 00:00:00",
        }
    ]

    expected_data_within_get_response(
        flask_test_client,
        "/applications?status_only=completed",
        expected_data,
    )

# TODO: Not possible to test all applications currently as unpredictable UID in default data
# def test_search_endpoint_get_applications_by_status(flask_test_client):
#     """
#     GIVEN We have a functioning Application Store API
#     WHEN a request for applications with a given status
#     THEN the response should only contain the applications that
#     have that status
#     """
#     expected_data = [
#         {
#             "id": "uuidv4-2",
#             "status": "NOT_STARTED",
#             "assessment_deadline": "2022-08-28 00:00:00",
#             "fund_id": "slugified_test_fund_name"
#         }
#     ]
#
#     exclude_regex_paths = r"root\[\d+\]\['id'\]"
#     expected_data_within_get_response(
#         flask_test_client,
#         "/applications"
#         "?status_only=not%20started",
#         expected_data,
#         exclude_regex_paths=exclude_regex_paths
#     )


def test_get_applications_by_id_contains(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications whose id's contain a given string
    THEN the response should only contain the applications that
    have ids that contain that string
    """
    expected_data = [
        {
            "id": "uuidv4-2",
            "status": "NOT_STARTED",
            "fund_id": "test-fund-name",
            "round_id": "spring",
            "date_submitted": "2022-12-25 00:00:00",
            "assessment_deadline": "2022-08-28 00:00:00",
        }
    ]

    expected_data_within_get_response(
        flask_test_client,
        "/applications?id_contains=v4-2",
        expected_data,
    )


# TODO: Not possible to test all applications currently as unpredictable UID in default data
# def test_search_endpoint_get_applications_sorted_by_rev_id(flask_test_client):
#     """
#     GIVEN We have a functioning Application Store API
#     WHEN a request for applications reverse sorted by id
#     THEN the response should return applications in the requested order
#     """
#     expected_data = [
#         {
#             "id": "uuidv4-2",
#             "status": "NOT_STARTED",
#             "assessment_deadline": "2022-08-28 00:00:00",
#             "fund_id": "slugified_test_fund_name"
#         },
#         {
#             "id": "uuidv4",
#             "status": "COMPLETED",
#             "assessment_deadline": "2022-08-28 00:00:00",
#             "fund_id": "slugified_test_fund_name"
#         }
#     ]
#
#     exclude_regex_paths = r"root\[\d+\]\['id'\]"
#     expected_data_within_get_response(
#         flask_test_client,
#         "/applications"
#         "?order_by=id&order_rev=1",
#         expected_data,
#         exclude_regex_paths=exclude_regex_paths
#     )


def test_get_application_by_application_id(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a GET /applications/<application_id> request is sent
    THEN the response should contain the application object
    """

    expected_data = {
        "id": "uuidv4",
        "status": "COMPLETED",
        "fund_id": "test-fund-name",
        "round_id": "spring",
        "date_submitted": "2021-12-24 00:00:00",
        "assessment_deadline": "2022-08-28 00:00:00",
        "questions": [
            {
                "question": "Q1",
                "status": "NOT STARTED",
                "fields": [
                    {
                        "key": "applicant_name",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "Applicant",
                    }
                ],
                "category": "",
                "index": 0,
            },
            {
                "question": "Q2",
                "status": "COMPLETED",
                "fields": [
                    {
                        "key": "applicant_name",
                        "title": "Applicant name",
                        "type": "text",
                        "answer": "Applicant",
                    }
                ],
                "category": "",
                "index": 0,
            },
        ],
        "metadata": {"paymentSkipped": "false"},
    }

    application_data = {
        "name": "Test Fund Name",
        "questions": [{"question": "A1"}],
    }
    post_data(flask_test_client, "/applications", application_data)

    i = 0
    while i < 200:
        post_data(flask_test_client, "/applications", application_data)
        i += 1

    expected_data_within_get_response(
        flask_test_client,
        "/applications/uuidv4",
        expected_data,
    )


def test_get_fund_applications_by_time_period(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a request for applications for a fund within a given time period
    THEN the response should only contain the applications for the fund
    that fall within the time period
    """
    expected_data = [
        {
            "id": "uuidv4-2",
            "status": "NOT_STARTED",
            "fund_id": "test-fund-name",
            "round_id": "spring",
            "date_submitted": "2022-12-25 00:00:00",
            "assessment_deadline": "2022-08-28 00:00:00",
        }
    ]

    expected_data_within_get_response(
        flask_test_client,
        "/applications"
        "?fund_id=test-fund-name&datetime_start=2022-01-01&datetime_end=2022-12-28",
        expected_data,
    )


def test_post_application_is_successful(flask_test_client):
    """
    GIVEN We have a functioning Application Store API
    WHEN a number of new application are posted
    THEN the application stores these applications within the correct fund
    """

    # Post one Funding Service Design application and check length
    application_data_a1 = {"name": "Funding Service Design", "questions": [{"question": "A1"}]}
    post_data(flask_test_client, "/applications", application_data_a1)

    expected_length_first_post = 2
    count_fund_applications(
        flask_test_client, "funding-service-design", expected_length_first_post
    )

    # Post second Fund B application and check length
    application_data_b2 = {"name": "Funding Service Design", "questions": [{"question": "A3"}]}
    post_data(flask_test_client, "/applications", application_data_b2)

    expected_length_second_post = 3
    count_fund_applications(
        flask_test_client, "funding-service-design", expected_length_second_post
    )

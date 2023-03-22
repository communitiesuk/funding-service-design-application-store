# How to run tests

1. Ensure that the environment variable DATABASE_URL is set to your db's connection string. The default during tests is:
   `postgresql://postgres:postgres@127.0.0.1:5432/fsd_app_store_test`, unless you manually set DATABASE_URL.
   - The command `invoke bootstrap-test-db --database-host=your-db-url` will create a db called "fsd_app_store_test".
2. Ensure you have installed the requirements-dev.txt
3. Run `pytest`

# Test Data
## Basic Usage - Individual application records
Test data is created on a per-test basis to prevent test pollution. To create test data for a test, request the `seed_application_records` fixture in your test. That fixture then provides access to the inserted records and will clean up after itself at the end of the test session.

More details on the fixtures in utils: https://github.com/communitiesuk/funding-service-design-utils/blob/dcc64b0b253a1056ce99e8fe7ea8530406355c96/README.md#fixtures

Basic example:

    @pytest.mark.apps_to_insert(
        [
            {
                "account_id": "user_a",
                "fund_id": "123",
                "language": "en",
                "round_id": "456",
            }
        ]
    )
    def test_stuff(seed_application_records):
      app_id = seed_application_records[0].id
      # do some testing

## Unique Fund and Round IDs - same for all applications
If you need all your test data to use the same fund and round ids, but be different from all other tests, use `unique_fund_round` in your test. This generates a random ID for fund and round and uses this when creating test applications.

    pytest.mark.apps_to_insert([test_application_data[0]])
    @pytest.mark.unique_fund_round(True)
    def test_some_reports(
        seed_application_records, unique_fund_round
    ):
        result = get_by_fund_round(
            fund_id=unique_fund_round[0], round_id=unique_fund_round[1]
        )

## Control how many funds/rounds/applications are created
If you need to seed the DB with a number of funds and rounds, each with a number of applications, request `seed_data_multiple_funds_rounds` in your test. This will generate a random fund ID and random round ID for each one requested, and insert the required number of applications. The following example will create 1 fund with 2 rounds, each containing 2 applications

    @pytest.mark.fund_round_config(
        {
            "funds": [
                {"rounds": [
                    {"applications": [{**app_data}, {**app_data}]},
                    {"applications": [{**app_data}, {**app_data}]}
                ]},
            ]
        }
    )
    def test_multi_funds(
        client, seed_data_multiple_funds_rounds
    ):
        result = get_all_apps_for_round(
            fund_id=seed_data_multiple_funds_rounds[0].fund_id,
            round_id=seed_data_multiple_funds_rounds[0].round_ids[0].round_id
        )
        assert 2 == len(result)

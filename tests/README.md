# How to run tests

1. Ensure that the environment variable DATABASE_URL is set to your db's connection string. The default during tests is:
   `postgresql://postgres:postgres@127.0.0.1:5432/fsd_app_store_test`, unless you manually set DATABASE_URL.
   - The command `invoke bootstrap-test-db --database-host=your-db-url` will create a db called "fsd_app_store_test".
2. Ensure you have installed the requirements-dev.txt
3. Run `pytest`

# Test Data
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

If you need to use a unique fund and round id in your test data (eg. for testing reports where the whole db is queried so test pollution can still impact), use `unique_fund_round` in your test. This generates a random ID for fund and round and uses this when creating test applications.

    pytest.mark.apps_to_insert([test_application_data[0]])
    @pytest.mark.unique_fund_round(True)
    def test_some_reports(
        seed_application_records, unique_fund_round
    ):
        result = get_by_fund_round(
            fund_id=unique_fund_round[0], round_id=unique_fund_round[1]
        )

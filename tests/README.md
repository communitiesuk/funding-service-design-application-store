# How to run tests

1. Ensure that the environment variable DATABASE_URL is set to your db's connection string. The default during tests is:
   `postgresql://postgres:postgres@127.0.0.1:5432/`, unless you manually set DATABASE_URL.
   - The command `invoke bootstrap-test-db --database-host=your-db-url` will create a db called "fsd_app_store_test".
2. Ensure you have installed the requirements-dev.txt
3. Run `pytest`

#!/usr/bin/env python3
import json
import subprocess
import sys
from os import environ

instance_index = json.loads(environ.get("VCAP_APPLICATION"))["instance_index"]
# Only run on first instance
if instance_index != 0:
    sys.exit(0)

environ["SQLALCHEMY_DATABASE_URI"] = environ.get("DATABASE_URL").replace(
    "postgres://", "postgresql://"
)

result = subprocess.run(["flask", "db", "upgrade"])
sys.exit(result.returncode)

poetry run sqlacodegen postgresql://${GCP_DB_USER}:${GCP_DB_PASSWORD}@${GCP_DB_HOST}:${GCP_DB_PORT}/${GCP_DB_NAME} > models.py

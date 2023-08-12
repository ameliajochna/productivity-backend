docker run \
    --env GCP_DB_USER=$GCP_DB_USER \
    --env GCP_DB_PASSWORD=$GCP_DB_PASSWORD \
    --env GCP_DB_HOST=$GCP_DB_HOST \
    --env GCP_DB_PORT=$GCP_DB_PORT \
    --env GCP_DB_NAME=$GCP_DB_NAME \
    -p 8080:8080 \
    europe-central2-docker.pkg.dev/avid-garage-390413/productivity-backend/productivity

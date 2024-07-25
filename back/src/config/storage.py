from google.cloud import storage

from config.environment import GCP_PROJECT_ID, GCS_BUCKET_NAME

client = storage.Client(project=GCP_PROJECT_ID)
bucket = client.get_bucket(GCS_BUCKET_NAME)

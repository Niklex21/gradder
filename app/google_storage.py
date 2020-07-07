from google.cloud import storage
from app.logs.form_logger import form_logger

def upload_blob(filename, file_obj):
    if filename and file_obj:
        storage_client = storage.Client()
        bucket = storage_client.bucket('gradder-storage')
        blob = bucket.blob(filename)
        blob.upload_from_file(file_obj)
        form_logger.info('File {} uploaded'.format(filename))
        return blob
    
def download_blob(filename, actual_filename):
    if filename:
        storage_client = storage.Client()
        bucket = storage_client.bucket('gradder-storage')
        blob = bucket.blob(filename)
        blob.download_to_filename(actual_filename)
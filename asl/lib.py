""" Utils and GCP APIs wrappers.
"""

import os

from google.cloud import storage


def extract_relative_path(root_path, path):
    """If root_path=/tmp/a and path=/tmp/a/b then return a/b."""
    root_path = os.path.abspath(root_path)
    subpath = path.replace(root_path, "").strip("/")
    basedir = os.path.basename(root_path)
    relative_path = os.path.join(basedir, subpath)
    return relative_path


def upload_directory_to_gcs(bucket_name, folder_path, bucket_prefix=None):
    """Upload directory to GCP bucket at bucket_prefix."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    for path, _, files in os.walk(folder_path):
        for name in files:
            path_local = os.path.join(path, name)
            blob_path = extract_relative_path(folder_path, path_local)
            if bucket_prefix:
                blob_path = os.path.join(bucket_prefix, blob_path)
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(path_local)


def download_directory_from_gcs(bucket_name, local_folder, bucket_prefix):
    """Download gs://bucket_name/a/b to local_folder/b (bucket_prefix=a/b)."""
    storage_client = storage.Client()
    local_folder = os.path.abspath(local_folder)
    if os.path.isdir(local_folder) is False:
        os.makedirs(local_folder)

    bucket = storage_client.bucket(bucket_name=bucket_name)
    blobs = bucket.list_blobs(prefix=bucket_prefix)

    for blob in blobs:
        blob_name = blob.name
        dst_file = os.path.join(
            local_folder,
            os.path.basename(bucket_prefix),
            blob_name.replace(bucket_prefix, "").strip("/"),
        )
        dst_dir = os.path.dirname(dst_file)
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        blob.download_to_filename(dst_file)

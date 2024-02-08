ZONE=us-central1-a
MACHINE_NAME=a100-notebook
MACHINE_TYPE=a2-highgpu-1g
IMAGE_FAMILY=tf-ent-2-12-gpu-debian-11-py310

while ! gcloud notebooks instances create $MACHINE_NAME \
    --vm-image-project=deeplearning-platform-release \
    --vm-image-family=$IMAGE_FAMILY \
    --machine-type=$MACHINE_TYPE \
    --location=$ZONE \
    --install-gpu-driver
do
    echo 'retry instance creation'
    sleep 5
done

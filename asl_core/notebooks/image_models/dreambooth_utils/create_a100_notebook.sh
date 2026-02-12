MACHINE_NAME=a100-notebook
ZONE=us-central1-a
MACHINE_TYPE=a2-highgpu-1g
IMAGE_PROJECT=cloud-notebooks-managed
IMAGE_FAMILY=workbench-instances
DISC_TYPE=PD_STANDARD

while ! gcloud workbench instances create $MACHINE_NAME \
    --vm-image-project=$IMAGE_PROJECT \
    --vm-image-family=$IMAGE_FAMILY \
    --machine-type=$MACHINE_TYPE \
    --install-gpu-driver \
    --boot-disk-type=$DISC_TYPE \
    --data-disk-type=$DISC_TYPE \
    --location=$ZONE
do
    echo 'retry instance creation'
    sleep 5
done

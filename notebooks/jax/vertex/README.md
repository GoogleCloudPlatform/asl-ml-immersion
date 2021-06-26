# JAX/Flax training and prediction on Vertex AI

[Flax](https://flax.readthedocs.io/en/latest/) is a deep learning library on top of [JAX](https://github.com/google/jax).

[Vertex AI](https://cloud.google.com/vertex-ai) is a suite of managed ML/AI services on Google Cloud. (Its core components at some points in time were also called _Cloud ML Engine_ and _AI Platform_.)

These examples use [Vertex AI Notebooks](https://cloud.google.com/vertex-ai/docs/general/notebooks), a managed JupyterHub environment that runs [Google Cloud Deep Learning VM Images](https://cloud.google.com/deep-learning-vm) and is tightly integrated with other Google Cloud products (for example, you can are pre-authenticated to directly run [`gcloud`](https://cloud.google.com/sdk/gcloud/reference) and [`gsutil`](https://cloud.google.com/storage/docs/gsutil) commands from Notebooks).

You can interact with Vertex AI in a number of ways, including the [Cloud Console GUI](https://console.cloud.google.com/), the [`gcloud ai` CLI](https://cloud.google.com/sdk/gcloud/reference/ai), [REST](https://cloud.google.com/vertex-ai/docs/reference/rest)/[RPC](https://cloud.google.com/vertex-ai/docs/reference/rpc) API calls, as well as a [client libraries in several languages](https://cloud.google.com/vertex-ai/docs/start/client-libraries). In the below examples we use the client library [Vertex SDK for Python](https://github.com/googleapis/python-aiplatform).

## Before you begin

The below examples were tested on Vertex Notebooks with a [Tensorflow Enterprise 2.5 GPU image](https://cloud.google.com/notebooks/docs/images#images). Install the [requirements.txt](requirements.txt) first.

```bash
python3 -m pip install --upgrade --user -r requirements.txt -f https://storage.googleapis.com/jax-releases/jax_releases.html
```

## Vertex AI Training

[Vertex AI Custom Training](https://cloud.google.com/vertex-ai/docs/training/custom-training) supports containerized ML training jobs, either using [pre-built containers](https://cloud.google.com/vertex-ai/docs/training/pre-built-containers) (that can only be lightly customized with e.g. additional Python packages) or with a [custom container](https://cloud.google.com/vertex-ai/docs/training/containers-overview).

The below examples all train the [FlaxMNIST](https://github.com/google/jax/blob/main/jax/experimental/jax2tf/examples/mnist_lib.py) model, optionally using a [GPU](https://cloud.google.com/gpu), and [`jax2tf`](https://github.com/google/jax/tree/main/jax/experimental/jax2tf) is used to convert to a [SavedModel](https://www.tensorflow.org/guide/saved_model), which is uploaded to [Cloud Storage](https://cloud.google.com/storage). Use a [TensorFlow 2.5 image](https://cloud.google.com/notebooks/docs/images#images) on [Vertex AI Notebooks](https://cloud.google.com/vertex-ai/docs/general/notebooks) to run.

- [training-prebuilt.ipynb](training-prebuilt.ipynb) uses a [pre-built container for TensorFlow](https://cloud.google.com/vertex-ai/docs/training/pre-built-containers#tensorflow) to train on Vertex AI. 

- [training-customcontainer.ipynb](training-customcontainer.ipynb) uses a [Google Cloud Deep Learning Container for TensorFlow](https://cloud.google.com/deep-learning-containers/docs/choosing-container) to train on Vertex AI.

- [training-local.ipynb](training-local.ipynb) trains the model inside the notebook environment (useful if you only want to explore Vertex AI prediction and need a SavedModel).

## Vertex AI Prediction

[Vertex AI Predition](https://cloud.google.com/vertex-ai/docs/predictions/getting-predictions) allows for many different types of ML models, including TensorFlow SavedModel artifacts, to be deployed to scalable endpoints that listen to online prediction requests. The uploaded models can also be used for batch prediction jobs.

- [prediction-customcontainer.ipynb](prediction-customcontainer.ipynb) uses a SavedModel stored in Cloud Storage, and bakes it in a [TensorFlow Serving container](https://www.tensorflow.org/tfx/serving/docker#creating_your_own_serving_image) which can be used as a [custom container for Vertex AI Prediction](https://cloud.google.com/vertex-ai/docs/predictions/use-custom-container).

## Next Steps

Many more things could be made possible with Vertex AI:

- Make GPU online prediction work
- Demonstrate [Batch Prediction](https://cloud.google.com/vertex-ai/docs/predictions/batch-prediction)
- [Distributed training](https://cloud.google.com/vertex-ai/docs/training/distributed-training)
- [Hyperparameter Tuning](https://cloud.google.com/vertex-ai/docs/training/hyperparameter-tuning-overview)
- [Experiments with managed TensorBoard](https://cloud.google.com/vertex-ai/docs/experiments)
- Orchestration with [Vertex Pipelines](https://cloud.google.com/vertex-ai/docs/pipelines), using Kubeflow Pipelines or TFX
- Further [MLOps](https://cloud.google.com/resources/mlops-whitepaper) components such as [Model Monitoring](https://cloud.google.com/vertex-ai/docs/model-monitoring)

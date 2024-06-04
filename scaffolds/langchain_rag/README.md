# Development Workflow

## Local development

The workflow described here works from CloudShell or any node with the [gcloud CLI](https://cloud.google.com/sdk/docs/install) has been properly installed and authenticated.

This means that you can develop your application locally on your laptop for example, as long as you have run `make auth` after installing the [gcloud CLI](https://cloud.google.com/sdk/docs/install) on it.

For local development, install the gcloud CLI following [these instructions](https://cloud.google.com/sdk/docs/install).

The first step is to set your GCP project and compute/zone variables:

```bash
gcloud config set compute/zone <YOUR_REGION>
gcloud config set project <YOUR_PROJECT>
```
The scripts in `./scripts` will use these variables. By default,
the app bucket name will be the same as the name of your  project.

**Caution:** Edit the `PROJECT`, `BUCKET`, and `LOCATION` variables in `app.yaml` to
match the configuration described above.


Authenticate your gcloud CLI for local development by running:

```bash
make auth
```

To enable the GCP services we need, and set up the permission to these services, please run:

```bash
make setup
```

The next step is to create and populate the virtual environment with

```bash
make venv
```
After this step you should find a new folder called `venv` containing the virtual environment.

Before running the app, you'll need to ingest the data and generate the embeddings that will be stored in `Chroma`; for that run

```bash
make ingest
````

At this point you should already be able to run the tests by running
```bash
make tests
```

To run the app locally, simply run
```bash
make run
```

At last to deploy the application on AppEngine run
```bash
make deploy
```

**Note:** `make clean` will remove all the built artifacts as long as the virtual environment created by `make venv`. This target is invoked by `make deploy` so that the built artifacts are not uploaded to AppEngine. The down-side is that the virtual environment will need to be recreated after each deployment.

## Development workflow

1. Edit the code
1. Run the tests with `make tests`
1. Test the app local with `make run`
1. Deploy the app on AppEngine with `make deploy`

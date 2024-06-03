# Development Workflow

## Local development

The workflow described here works from CloudShell or any node with the [gcloud CLI](https://cloud.google.com/sdk/docs/install) has been properly installed and authenticated.

This means that you can develop your application fully locally on your laptop for example, as long as you have run `make auth` after installing the [gcloud CLI](https://cloud.google.com/sdk/docs/install) on it.

For local development, install then the gcloud CLI following [these instructions](https://cloud.google.com/sdk/docs/install).

The first step is to set you SDK project and compute/zone variables:
```bash
gcloud config set compute/zone <YOUR_REGION> 
gcloud config set project <YOUR_PROJECT> 
```
The scripts in `./scripts` will you use these variables. By default,
the app bucket name will be the same as your project name.

**Caution:** Edit the `PROJECT`, `BUCKET`, and `REGION` variables in `app.yaml` to 
match the configuration described above.


Make sure to accept upgrading Python to 3.10 if prompted, then authenticate for local development by running:

```bash
make auth
```

To enable the GCP services we need, and setup the permission to these services, please run:
```bash
make setup
```

The next step is to create and populate the virtual environment with

```bash
make venv
```
After this step you should find a new folder called `venv` containing the virtual environment.

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

# Developpment Workflow 


## Local developpment

The workflow described here works from CloudShell or any node with the gcloud SDK authenticated
,that is, you can do the developpement fully locally on your laptop, which is the preferred
development environment.

For local development, first install the Google SDK following these instructions(https://cloud.google.com/sdk/docs/install#mac).
Make sure to accept upgrading Python to 3.10 when prompted, then authenticate for local development by running:
```bash
make auth
```

Then create and populate the virtual environment:
```bash
make venv
```

To run the tests:
```bash
make tests
```

Run the answernaut locally with
```bash
make run
```

Deploy on AppEngine
```bash
make deploy
```

## Developpement workflow

1. Edit the code
1. Run the tests with `make tests`
1. Test the app local with `make run`
1. Deploy the app on AppEngine with `make deploy`

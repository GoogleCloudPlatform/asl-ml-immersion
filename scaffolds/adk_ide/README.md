# Quick Start (Local Testing)

Install required packages and launch the local development environment:

```bash
cd scaffolds/adk_ide
cp env.example .env
#vim .env # Uncomment and update the environment variables
```

If you are using Vertex AI, make sure you are authenticated with `gcloud`:

```bash
gcloud auth application-default login
gcloud config set project <your-dev-project-id>
make install
make playground
```

# Dev Environment

You can test deployment towards a Dev Environment using the following command:

```bash
make backend
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch local development environment with backend and frontend - leveraging `adk web` command.|
| `make backend`       | Deploy agent to Cloud Run |

For full command options and usage, refer to the [Makefile](Makefile).

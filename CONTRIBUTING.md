Unfortunately we are not accepting external contributions at this time, sorry.

_For maintainers:_

## `pre-commit`

### TLDR

If the `pre-commit.ci` check fails, please install and run `pre-commit` in your development environment as follows, accept auto-fixes and resolve any issues, and re-commit.

```bash
python3 -m pip install pre-commit
cd ~/asl-ml-immersion  # or wherever your repo is
pre-commit install
pre-commit run --all-files
# fix any issues that weren't auto-fixed, such as `pylint` issues
git commit -a -m "pre-commit"
```

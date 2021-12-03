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

### Intro: Linters

Linters are tools that check your code for syntax errors as well as PEP8 style violations, and either report any issues (such as `pylint`) or sometimes even automatically fix your code (such as `black` does). Please see the [Pylint tutorial](https://pylint.pycqa.org/en/latest/tutorial.html), and the [Black documentation](https://black.readthedocs.io/en/stable/index.html)).

It is common practice to instead of choosing one linter, run multiple different linters one after the other on your code, and let each of them do their own job. Of course, you should not have conflicting rules in this case, such as different preferred max line lengths.

Note that there is an externally published Google `pylint` configuration file linked to [Google's external Python Style Guide](https://google.github.io/styleguide/pyguide.html#21-lint), and this is copied to this repo's root.

#### Linters on Jupyter Notebooks

It is trickier to run linters on notebooks than on simple `.py` text files, but not impossible. First of all, one could just output a notebook as a Python script with [`jupyter nbconvert --to script`](https://nbconvert.readthedocs.io/en/latest/usage.html) and run linters on the output.

However there are luckily other tools that wrap around such a process, as well as handle notebook idiosyncracies such as magic cells: [nbQA](https://nbqa.readthedocs.io/en/latest/index.html) and recently even built in to [Black](https://black.readthedocs.io/en/stable/change_log.html?highlight=jupyter#id5).





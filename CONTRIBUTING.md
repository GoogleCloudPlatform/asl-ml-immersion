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

### Intro: pre-commit

[pre-commit](https://pre-commit.com/) allows you to define a set of passive checks or active automatic re-formats, that are executed if you request a `git commit`, and your commit is only successful, if all of these checks successfully complete. If `pre-commit` does edit your files, your commit is aborted and you have the chance to verify these changes before you'd commit again.

This set of hooks is defined in the repository root in a `.pre-commit-config.yaml` file. This config will only actually be used during your commits if you first install pre-commit (both in general in your environment and specifically for your current repo):

```bash
python3 -m pip install pre-commit
cd ~/asl-ml-immersion  # or wherever your repo is
pre-commit install
```

During a commit, `pre-commit` only checks your changed files. If you would like to run pre-commit on the whole repository, you can do so:

```bash
pre-commit run --all-files
```

### Intro: pre-commit.ci

`pre-commit` on its own relies on each contributor to have it installed in their local environments. It is even better if PR's are also checked once more at the GitHub side. This is made possible by [pre-commit.ci](https://pre-commit.ci/), that is availble at no cost for public repositories as a GitHub Check and it is installed for this repository.

One thing to note is that while developer-side pre-commit checks run on the changeset, the CI check runs on the whole repo. Therefore, in order to fix a failing pre-commit.ci, you need to run pre-commit on the whole repo on your end with `pre-commit run --all-files`, and also fix issues in files beyond your changeset.

(pre-commit.ci actually comes with the capability to automatically commit changes, but this is intentionally switched off with `autofix_prs: false` as it causes the Google CLA check to fail.)

### Putting it together

This repo's `.pre-commit-config.yaml` includes:
- a set of small hooks available as part of pre-commit, in [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks/tree/master/pre_commit_hooks), such as [trailing-whitespace](https://github.com/pre-commit/pre-commit-hooks#trailing-whitespace) to remove trailing whitespace.
- the passive linter `pylint` which in turn uses `pylintrc` in the root which is the copy of the public Google `pylintrc` from [here](https://google.github.io/styleguide/pyguide.html#21-lint).
- the active linter `black`, as well as its jupyter-compatible flavors `nbqa-black` and `black-jupyter`.
- the specialized linters `isort` and `pyupgrade` (including their `nbqa` versions), that update import statement orders, and Python 2/3 compatibility code pieces, respecitvely.

### FAQ

#### _How can I ask `pylint` to ignore something?_

With comments like `# pylint: disable=[rule]`, see [the docs](https://pylint.pycqa.org/en/latest/user_guide/message-control.html).

#### _Can I disable pre-commit or pre-commit.ci?_

The short answer is "yes", but the longer answer is that "you shouldn't".

You can run a commit without any pre-commit checks by `git commit --no-verify`.

You can also disable precommit-ci by including `[skip ci]` in the commit message.

However, if you push through such a change, that means pre-commit.ci checks will most probably fail for all further commits until eternity, so you should actually resolve this state asap.

You have a few options:
- You can ask most linters to ignore parts of you code, such as in the `pylint` question above.
- You can include an [`exclude`](https://pre-commit.com/#top_level-exclude) pattern in the `.pre-commit-config.yaml` to exclude a whole file.
- You can modify `.pre-commit-config.yaml` to globally ignore certain rules, there are already such rules in the current config.
- If a hook is really misbehaving, you could remove that specific hook, while leaving the other hooks in place.

#### _For educational reasons, I write purposefully incomplete Python code, which fails syntax checks. What to do?_

Syntax errors understandably trip multiple checks. The best way is to try to rewrite your incomplete code in a way that it is syntactically correct:

```python
# instead of:
variable =  # TODO

# use this:
variable = None  # TODO
```

```python
# instead of:
function_name( # TODO

# use this:
function_name(
    # TODO
)
```

However if you must exclude a file, you can do it with the [`exclude`](https://pre-commit.com/#top_level-exclude) pattern. See also the "_Can I disable pre-commit?_" question answers.

#### _I see a PR generated by `pre-commit.ci` with the word `autoupdate`, what is this?_

pre-commit.ci comes with an autoupdate feature that cannot be disabled, it runs at least once a quarter (see in the config file `autoupdate_schedule: quarterly`).

You can either accept and merge this PR, or if you probably don't want the Google CLA check to be failing, then create your own branch, run `pre-commit autoupdate`, and commit and merge the results, and delete the original PR.

#### _pre-commit.ci is failing because `nbqa-black` and `black-jupyter` disagree (and maybe it worked fine locally)_

`nbqa-black` uses your local version of `black` (meaning the latest version on the server side), and this can clash with the `black` version pinned in the `pre-commit-config.yaml`.

The solution is to upgrade your local `black` (such as `pip install --upgrade black`), run `pre-commit autoupdate` and push the changes.

(In theory there would be a solution, in the pre-commit-config.yaml file in the nbqa-black section one could add something like `additional_dependencies : ['black:21.12b0']` ([see also the same advice in the nbQA doc](https://github.com/nbQA-dev/nbQA#pre-commit)), but probably this would add an unnecessary layer of manual maintenance burden (e.g. having to manually bump this version and sync with `black`'s).)

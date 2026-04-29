# format-olca-json

## Usage

Add the following to your `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/a-w-beck/format-olca-json.git
  rev: v0.1.0
  hooks:
    - id: format-olca-json
```

Build and activate a Python virtual environment[^1], then run `pre-commit install` to implement the hook.


For first-time `pre-commit` users, I highly recommend [Stefanie Molin's pre-commit setup guide](https://stefaniemolin.com/articles/devx/pre-commit/setup-guide/)*

### Test Run

Once the hook is installed on your repo, test that it is working:

1. Drop a single-line .JSON file into the repo

2. Stage and commit the file. A series of `[INFO]` log statements should now appear—one for each pre-commit hook installed on your repo—and resolve with "Passed" or "Failed" statuses.

3. Since your single-line .JSON was not already in the preferred format, you should see a "Failed" statement for the `Format openLCA JSON` hook. Open and inspect the file to verify that it was formatted as expected.

## Customization

The `format-olca-json` hook supports command-line arguments such as `--preview`, which prints to console the changes that would be made to staged JSON rather than automatically applying the changes:

```yaml
- repo: https://github.com/a-w-beck/format-olca-json.git
  rev: v0.1.0
  hooks:
    - id: format-olca-json
      args: [--preview]
```

For additional configurations, refer to the [pre-commit documentation](https://pre-commit.com/#pre-commit-configyaml---hooks).


[^1]: For example, with [pixi](https://pixi.prefix.dev/) already installed, copy the `pyproject.toml` from this repo into your project repo and run `pixi shell -e dev` to build the env and initialize a shell session within it.

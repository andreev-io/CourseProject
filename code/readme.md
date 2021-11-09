# Dev Workflow

- Install [poetry](https://python-poetry.org/) to manage our environment across systems
- Add new dependencies by running `poetry add <dependency-name>`
- Run `poetry shell` to spawn a shell in the virtual environment managed by poetry, which should be consistent across all systems.
- Document commands used to run any scripts as a part of pull requests, to ensure that results can be replicated across the team.

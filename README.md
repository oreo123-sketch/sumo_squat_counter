# ObsChart Python Backend

## Usage

```bash
# Install Poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# Clone project
git clone git@gitlab.com:deepscope/obschart-py-backend.git
cd obschart-py-backend

# Setup project
cp .env.example .env
poetry install

# Run
poetry run python -m obschartpybackend
```

## Notes

- Use VSCode and install recommended extensions if you can
- Run `./scripts/test.sh` before you push to see if there's anything wrong with your code

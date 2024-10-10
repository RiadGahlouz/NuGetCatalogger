# NuGetCatalogger
This little tool can be used to download all NuGet Catalog pages (around 20k on Oct 10, 2024), parse them and generate a registry with all NuGet packages as well as links for package information for every version of the package.

# How to Run
## Generate the registry
1. First step is to create a Python Virtual Environment. Install `venv`:\
`python -m pip install venv`

1. Initialize the environment:\
`python -m venv .venv`

1. Activate the environment:\
`source ./.venv/bin/activate`

1. Install the required dependencies:\
`pip install requirements.txt`

1. Run the tool and enjoy:\
`python GenerateRegistry.py`

## Run the WebAPI
There is a little Flask web api to query the registry. If you run the `RegApi.py` script, you will be able to query the api at the url `http://127.0.0.1:5000/package/{packageIdInLowerCase}`



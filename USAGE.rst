=====
Usage
=====


To develop on mapscookiegettercli:

.. code-block:: bash

    # The following commands require pipenv as a dependency

    # To lint the project
    _CI/scripts/lint.py

    # To execute the testing
    _CI/scripts/test.py

    # To create a graph of the package and dependency tree
    _CI/scripts/graph.py

    # To build a package of the project under the directory "dist/"
    _CI/scripts/build.py

    # To see the package version
    _CI/scripts/tag.py

    # To bump semantic versioning [--major|--minor|--patch]
    _CI/scripts/tag.py --major|--minor|--patch

    # To upload the project to a pypi repo if user and password are properly provided
    _CI/scripts/upload.py

    # To build the documentation of the project
    _CI/scripts/document.py


To use mapscookiegettercli:

    # For this to work python3.7 and pipenv should be available

.. code-block:: bash

    # Make pipenv use local directory
    export PIPENV_VENV_IN_PROJECT=true

    # Clone the repository
    git clone https://github.com/costastf/mapscookiegettercli.git

    # Switch to working branch
    git checkout initial-usability

    # Source helper tools
    source setup_aliases.sh

    # Build artifact
    # This will setup a new virtual environment, install all dependencies and build the artifact
    _build

    # Install built artifact
    # This will create a new virtual environment installing the artifact and all required dependencies.
    pipenv install dist/mapscookiegettercli-0.0.0.tar.gz

    # Activate the virtual environment
    _activate

    # execute the tool
    maps-cookie-getter

    # After the full login process the browser should be terminated and a "location_sharing.cookies"
    # file should be located at the same location that can be provided to the locationsharinglib.

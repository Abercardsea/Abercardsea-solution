# CodingChallengeSolution

[![Run tests](https://github.com/Abercardsea/Abercardsea-solution/actions/workflows/pytest.yaml/badge.svg)](https://github.com/Abercardsea/Abercardsea-solution/actions/workflows/pytest.yaml)
[![codecov](https://codecov.io/gh/Abercardsea/Abercardsea-solution/branch/main/graph/badge.svg?token=CFARAVMGZU)](https://codecov.io/gh/Abercardsea/Abercardsea-solution)

 development repo for the coding challenge solution.

# First time set-up

Got into bidder/src and make a copy of the config_example.py file and rename it to config.py. You need to add your API keys into this file. It will then be read from the API moduls when needed. You should keep this file private and not shared on github for security reasons.


The requirement.txt file here is for pytest to run tests, and should be all the dependicies needed to run the application.

Run docker:
```bash
docker build -t bidder-container .
docker run -it bidder-container sh
```

This will start the container after installing all dependecies.
The program isnt running yet. If there is no database present.

```bash
./start_bidder.sh
```

If there is a database present.

```bash
python -m bidder
```

# Server.

Currently there is no server running. (So no dashboard etc. )
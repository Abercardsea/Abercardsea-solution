# CodingChallengeSolution

[![Run tests](https://github.com/Abercardsea/Abercardsea-solution/actions/workflows/pytest.yaml/badge.svg)](https://github.com/Abercardsea/Abercardsea-solution/actions/workflows/pytest.yaml)
[![codecov](https://codecov.io/gh/Abercardsea/Abercardsea-solution/branch/main/graph/badge.svg?token=CFARAVMGZU)](https://codecov.io/gh/Abercardsea/Abercardsea-solution)

 development repo for the coding challenge solution.

# First time set-up

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
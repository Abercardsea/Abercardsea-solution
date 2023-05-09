# CodingChallengeSolution
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
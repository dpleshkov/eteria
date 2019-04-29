# Eteria

Eteria is my attempt to make a production-ready multiplayer io game. The current test server can be found on https://eteria.herokuapp.com . I am constantly optimizing internal and client code so that the game does not "lag". Right now the game may seem barren and very simplistic, but I am planning to add features and mechanics once the optimization issues are fixed.


## Running Your Own Server

* Make sure you have Python 3 installed on your computer

* Download the repository using `git clone https://github.com/dpleshkov/eteria.git` or by using the "Download ZIP" button.

* Navigate to the folder in your terminal using `cd`

* Run `python3 -m pip install -r requirements.txt` to install the libraries needed

* Finally, run `python3 app.py` to start the game server. In your browser, navigate to `http://localhost:5000` to play. Others on your local network may also play by going to `http://<YOUR IP>:5000`.

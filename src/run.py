from app import app
from os import environ

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = environ["PORT"]
    print("Server running on {}:{}".format(HOST, PORT))
    app.run(host="localhost", port=PORT)

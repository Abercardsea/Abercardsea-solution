from server import create_app

# create app Web server backend, not required to solution to run.

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
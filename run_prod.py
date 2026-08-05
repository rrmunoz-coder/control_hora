from waitress import serve
from atlas import create_app

app = create_app()

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=app.config["ATLAS_PORT"], threads=8)

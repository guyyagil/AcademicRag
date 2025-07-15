from flask import Flask
from api.endpoint import api
from api.swagger import init_swagger
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
app.json.sort_keys = False

app.register_blueprint(api, url_prefix='/api')  # Register API routes
init_swagger(app)  # Initialize Swagger docs (set to /swagger/)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

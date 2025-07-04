from flask import Flask
from api.endpoint import api
from api.swagger import init_swagger

app = Flask(__name__)
init_swagger(app)  # Enable Swagger UI

app.register_blueprint(api, url_prefix='/api')

# ...existing code...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
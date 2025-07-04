from flasgger import Swagger

def init_swagger(app):
    """
    Initialize Swagger UI for the given Flask app.
    """
    swagger = Swagger(app)
    return swagger

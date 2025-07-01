from fastapi_microservice import app
from mangum import Mangum

handler = Mangum(app) 
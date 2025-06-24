from fastapi import FastAPI
from agents.backend_ads.email_sequence.api import router

app = FastAPI()
app.include_router(router)

for route in app.routes:
    print(route.path)

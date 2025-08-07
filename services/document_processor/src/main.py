from api.routes import router
from fastapi import FastAPI

app = FastAPI(title="Document Processor")
app.include_router(router)
import os
import numpy as np
from fastapi import FastAPI
from dependencies import lifespan
from routers import router

# 환경 변수
os.environ["MKL_THREADING_LAYER"] = "GNU"

app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    import multiprocessing as mp
    mp.set_start_method("spawn", force=True)

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)  

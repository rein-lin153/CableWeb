# test_static.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

print(f"挂载目录: {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    return {"msg": "Hello World"}
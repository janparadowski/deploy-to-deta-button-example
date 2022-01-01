import os
from fastapi import FastAPI, Response
import requests

app = FastAPI()

@app.get("/")
async def index(name: str = "World"):
	y = os.environ
	z = f"now running some python code {y}"
	#name = os.getenv("NAME", "world")
	return f"hello {name}! {z}"

@app.get("/junction")
async def get_junction():
	content = requests.get("https://dev.junction.app/server/ping").text
	return Response(content=content, media_type="text/html")

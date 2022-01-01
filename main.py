import os, requests
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/")
async def index(name: str = "World"):
	y = os.getenv('MY_SECRET', "non such secret")
	z = f"now running some python code {y}"
	return f"hello {name}! {z}"

@app.get("/junction")
async def get_junction():
	content = requests.get("https://dev.junction.app/server/ping").text
	return Response(content=content, media_type="text/html")

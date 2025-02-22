import os, requests, base64, hmac, hashlib, json, datetime
from fastapi import FastAPI, Response, Request

app = FastAPI()

def smack(a,b):
    return hmac.new(a, b.encode('utf-8'), hashlib.sha256).digest()

def base64encode(a):
    return base64.b64encode(json.dumps(a).encode()).decode()

def s3upload(hostname):
    (access, secret) = os.getenv('MY_SECRET').split(":")

    date = datetime.datetime.utcnow()
    expiration = date + datetime.timedelta(minutes=10)
    expiration = expiration.strftime("%Y-%m-%dT%H:%M:%SZ")
    date = date.strftime("%Y%m%d")
    region = "us-east-2"
    credentials = f"{access}/{date}/{region}/s3/aws4_request"
    redirect = f"https://{hostname}/success"
    bucket = "folly-user-media"
    
    t = smack(("AWS4" + secret).encode('utf-8'), date)
    t = smack(t, region)
    t = smack(t, "s3")
    t = smack(t, "aws4_request")
    date = f"{date}T000000Z"
    
    policy = {
        "expiration": expiration,
        "conditions": [
            {"bucket": bucket},
            {"acl": "public-read"},
            ["starts-with", "$key", ""],
            {"success_action_redirect": redirect},
            {"x-amz-server-side-encryption": "AES256"},
            {"x-amz-credential": credentials},
            {"x-amz-algorithm": "AWS4-HMAC-SHA256"},
            {"x-amz-date": date}
        ]
    }
    policy = base64encode(policy)
    signature = hmac.new(t, policy.encode('utf-8'), hashlib.sha256).hexdigest()
    return dict(
        redirect = redirect,
        bucket = bucket,
        signature = signature,
        date = date,
        policy = policy,
        credentials = credentials
    )

@app.get("/iframe")
async def iframe(request: Request):
    template = """
    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      </head>
      <body>
      This works for 10 mins after (re-)loading the page.<br/>
      <form action="https://{bucket}.s3.amazonaws.com/" method="post" enctype="multipart/form-data">
        <input type="hidden" name="acl" value="public-read" />
        <input type="hidden" name="success_action_redirect" value="{redirect}" />
        <input type="hidden" name="x-amz-server-side-encryption" value="AES256" /> 
        <input type="hidden" name="X-Amz-Algorithm" value="AWS4-HMAC-SHA256" />
        <input type="hidden" name="key" value="${{filename}}" />
        <input type="hidden" name="Policy" value="{policy}"/>
        <input type="hidden" name="X-Amz-Signature" value="{signature}" />
        <input type="hidden" name="X-Amz-Credential" value="{credentials}" />
        <input type="hidden" name="X-Amz-Date" value="{date}" />
        <input type="file"   name="file" /> <br />
        <input type="submit" name="submit" value="Upload to Amazon S3" />
      </form>
    </body>
    </html>
    """
    vars = s3upload(request.url.hostname)
    template = template.format(**vars)
    return "Not exposed"
    return Response(content=template, media_type="text/html")

@app.get("/success")
async def success():
    return "Uploaded"

@app.get("/")
async def index(request: Request, name: str = "World"):
    host = request.url.hostname
    return f"hello {name}! {host}"

@app.get("/junction")
async def get_junction():
    content = requests.get("https://dev.junction.app/server/ping").text
    return Response(content=content, media_type="text/html")

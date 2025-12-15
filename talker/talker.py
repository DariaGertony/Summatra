import uvicorn
from fastapi import FastAPI, Request
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv()



app = FastAPI()

token = os.environ.get("TOKEN", "empty")
if(token=="empty"):
    print("Send tg bot token")
    token = input()
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=token,
)


@app.post("/translator")
async def translator(request: Request):
    body = await request.json() 
    text = body["data"]
    print(text)
    lang = body["lang"]
    response = client.chat.completions.create(
      model="arcee-ai/trinity-mini:free",
      messages=[
        {
          "role": "user",
          "content": body["data"] + " translate all this to "+ body["lang"] + "\n write only the most appropriate translation without your comments follow the structure of input",
        }
      ]
    )
    print(response.choices[0].message.content)
    return {"translation": response.choices[0].message.content}


@app.post("/summer")
async def summer(request: Request):
    print("here")
    body = await request.json() 
    text = body["data"]
    response = client.chat.completions.create(
      model="arcee-ai/trinity-mini:free",
      messages=[
        {
          "role": "user",
          "content": body["data"] + "\n write a short summary on this, write only plain text without .md symbols",
          
        }
      ]
    )
    print(response.choices[0].message.content)
    return {"summary": response.choices[0].message.content}

@app.post("/memmer")
async def memmer(request: Request):
    print("here")
    body = await request.json() 
    text = body["image"]
    source = body["source"]
    print(source)
    response = client.chat.completions.create(
      model="amazon/nova-2-lite-v1:free",
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": f"Tell me shortly about this meme from {source} without .md symbols add 3 best one-word tags (not connected with word 'meme' or 'humour') at the end in format like |tag1|tag2|tag3|"
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{text}"
              }
            }
          ]
        }
      ]
    )
    print(response.choices[0].message.content)
    return {"summary": response.choices[0].message.content}


if __name__ == '__main__':
    uvicorn.run(app,  host="0.0.0.0", port=3456)
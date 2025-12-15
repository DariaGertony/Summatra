import uvicorn
from fastapi import FastAPI, Request
import psycopg
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
import os



host = os.environ.get("PG_HOST", "empty")
port = os.environ.get("DB_PORT", "empty")
user = os.environ.get("POSTGRES_USER", "empty")
dbname = os.environ.get("POSTGRES_DB", "empty")
password = os.environ.get("POSTGRES_PASSWORD", "empty")
if("empty" in (host, port, user, dbname, password)):
    print("send db info: host, port, dbname, user, password")
    host, port, dbname, user, password = input().split()



pool = AsyncConnectionPool(f"host={host} port={port} dbname={dbname} user={user} password={password}",
    open=False, 
    max_size=20
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open()
    async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("CREATE TABLE IF NOT EXISTS memes(id SERIAL PRIMARY KEY, name TEXT, data TEXT, tag1 TEXT, tag2 TEXT, tag3 TEXT);")
    print("tablet")
    yield
    await pool.close()

    



app = FastAPI(lifespan=lifespan)

@app.get("/items")
async def read_items():
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name, tag1, tag2, tag3 FROM memes;")
            items = await cur.fetchall()
            return {"items": items}
        

@app.get("/tag/{tag}")
async def getbytag(tag):
     async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name, tag1, tag2, tag3 FROM memes WHERE tag1=%s OR tag2=%s OR tag3=%s;", (tag,tag,tag))
            items = await cur.fetchall()
            return {"items": items}

@app.get("/name/{name}")
async def getbyname(name):
     async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name, tag1, tag2, tag3 FROM memes WHERE name=%s;", (name,))
            items = await cur.fetchall()
            return {"items": items}
        
@app.get("/id/{name}")
async def getbyid(name):
     async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT name, data FROM memes WHERE id=%s;", (name,))
            items = await cur.fetchall()
            return {"items": items}

@app.post("/addmeme")
async def addmeme(request: Request):
    meme = await request.json()
    print(meme.get("tags"))
    async with pool.connection() as conn:
        await conn.execute(
            """
            INSERT INTO memes (name, data, tag1, tag2, tag3) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (meme.get("name"," "),
            meme.get("data"," "),
            meme.get("tags",['','',''])[0],
            meme.get("tags",['','',''])[1],
            meme.get("tags",['','',''])[2])
        )
        return {"status": "success"}


if __name__ == '__main__':
    uvicorn.run(app,  host="0.0.0.0", port=3434)
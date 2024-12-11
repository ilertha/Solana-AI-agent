import uuid
from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from pydantic import BaseModel
from pymongo import MongoClient
import pymongo
from sse_starlette.sse import EventSourceResponse
from datetime import datetime as dt
from solana_agent.config import config
from solana_agent.services.chat_service import chat_service
import jwt

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB client
client = MongoClient(config.MONGO_URL)
db = client[config.MONGO_DB]


class ChatRequest(BaseModel):
    text: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        config.NEXTAUTH_URL,
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["*"],
)


async def check_bearer_token(authorization: str = Header(...)):
    # get bearer token from header
    token = authorization.split("Bearer ")[1]

    try:
        jwt_fields = jwt.decode(token, config.NEXTAUTH_SECRET, algorithms=["HS256"])

        if jwt_fields["issuer"] != config.NEXTAUTH_URL:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized",
            )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )
    return jwt_fields


@app.get("/history/{user_id}")
async def history(
    user_id: str, page_num: int, page_size: int, token=Depends(check_bearer_token)
):
    if token.get("sub") != user_id:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    try:
        skips = page_size * (page_num - 1)
        total_items = len(db.messages.find({"user_id": user_id}).to_list(None))
        cursor = (
            db.messages.find({"user_id": user_id})
            .sort("timestamp", pymongo.DESCENDING)
            .skip(skips)
            .limit(page_size)
        )
        items = []
        for document in cursor:
            items.append(
                {
                    "id": str(document["_id"]),
                    "message": document["message"],
                    "response": document["response"],
                    # convert datetime string timestamp to unix timestamp
                    "timestamp": int(dt.timestamp(document["timestamp"])),
                }
            )
        return {
            "data": items,
            "total": total_items,
            "page": page_num,
            "page_size": page_size,
            "total_pages": total_items // page_size + (total_items % page_size > 0),
        }
    except Exception:
        return {
            "data": [],
            "total": 0,
            "page": page_num,
            "page_size": page_size,
            "total_pages": 0,
        }


@app.get("/sse/{user_id}/{conversation_id}")
async def sse_endpoint(user_id: str, conversation_id: str, request: Request):
    conversation = db.conversations.find_one(
        {"user_id": user_id, "conversation_id": conversation_id, "status": "active"}
    )
    if not conversation:
        return {
            "error": "No active conversation found for this user_id and conversation_id"
        }

    queue = asyncio.Queue()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                event = await queue.get()
                yield event
                queue.task_done()
                if event["event"] == "close":
                    break
        except Exception as e:
            logger.error(f"Error in event generator: {str(e)}")
            yield {"event": "error", "data": str(e)}
            yield {"event": "close", "data": ""}

    async def message_producer():
        try:
            async for text in chat_service.generate_response(
                user_id, conversation["last_message"]
            ):
                await queue.put({"event": "message", "data": text})
                await asyncio.sleep(0.1)  # Small delay to ensure chunked response

            # Send a close event
            await queue.put({"event": "close", "data": ""})

            # Update conversation status to "completed" in MongoDB
            db.conversations.update_one(
                {"user_id": user_id, "conversation_id": conversation_id},
                {"$set": {"status": "completed"}},
            )
        except Exception as e:
            logger.error(f"Error in message producer: {str(e)}")
            await queue.put({"event": "error", "data": str(e)})
            await queue.put({"event": "close", "data": ""})

    # Start the message producer task
    asyncio.create_task(message_producer())

    return EventSourceResponse(event_generator())


@app.post("/chat/{user_id}")
async def start_conversation(
    user_id: str, chat: ChatRequest, token=Depends(check_bearer_token)
):
    if token.get("sub") != user_id:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )
    conversation_id = str(uuid.uuid4())  # Generate a unique conversation ID
    db.conversations.insert_one(
        {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "status": "active",
            "last_message": chat.text,
            "created_at": dt.now(),
        }
    )
    return {
        "message": "Conversation started. Connect to SSE endpoint to receive updates.",
        "conversation_id": conversation_id,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

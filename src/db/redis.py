import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY = 3600

# Kết nối Redis sử dụng `redis.asyncio`
token_blocklist = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
    decode_responses=True,  # Để tránh lỗi trả về byte-string
)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    return await token_blocklist.exists(jti)  # Trả về True nếu token tồn tại

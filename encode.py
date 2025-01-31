import jwt
import datetime

SECRET_KEY = "your_secret_key"

payload = {
    "user_id": 123,
    "username": "johndoe",
    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print(token)

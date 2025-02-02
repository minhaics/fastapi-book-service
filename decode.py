import jwt
SECRET_KEY = "your_secret_key"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiam9obmRvZSIsImV4cCI6MTczODMwMjk2MX0.dKSI3A34laXBZ7PiVg9PkvuiEd_MEwxaCfQGBX2HHZg"
decoded = jwt.decode(
                    token, 
                    algorithms=["HS256"], 
                    key= SECRET_KEY
                    )
print(decoded)

#    raise InvalidSignatureError("Signature verification failed")
# jwt.exceptions.InvalidSignatureError: Signature verification failed

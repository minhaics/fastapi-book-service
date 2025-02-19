from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from src.auth.utils import create_access_token, verify_password, generate_password_hash
from src.db.redis import add_jti_to_blocklist
from .schemas import PasswordResetConfirmModel, PasswordResetRequestModel, UserCreateModel, UserModel, UserLoginModel, UserBooksModel, EmailModel, UserResponseModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from .dependencies import AccessTokenBearer, RefreshTokenBearer, get_current_user_in_token, RoleChecker
from src.auth.utils import create_url_safe_token, decode_url_safe_token
from src.config import Config
from src.errors import UserNotFound, UserAlreadyExists
from src.mail import create_message, mail
from src.celery_tasks import send_email

auth_router = APIRouter()
user_service = UserService()
role_checker= RoleChecker(['admin', 'user'])

REFRESH_TOKEN_EXPIRY = 2

from fastapi import BackgroundTasks

@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data= {"email": user.email, "user_uid": str(user.uid)}
            )
            refresh_token = create_access_token(
                user_data= {"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )
            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email Or Password"
    )

@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Or expired token"
    )

@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content= {"message": "Logged Out Successfully"}, 
        status_code=status.HTTP_200_OK
    )

@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user= Depends(get_current_user_in_token), 
    _: bool = Depends(role_checker)
):
    return user

@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):

    token_data: dict = decode_url_safe_token(token)
    user_email = token_data.get("email")
    
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )
        
    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(
    user_data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Create user account using email, username, first_name, last_name
    params:
        user_data: UserCreateModel
    """
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """

    emails = [email]

    subject = "Verify Your email"

    send_email.delay(emails, subject, html)  # changed to this

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }

@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    send_email.delay([email], subject, html_message)  # changed to this

    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )

@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        passwd_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)
        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@auth_router.post("/send-mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"
    send_email.delay(emails, subject, html)  # changed to this
    return {"message": "Email sent successfully"}

from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status

from app.core.config import settings
from app.core.database  import get_db
from app.models.user import User


from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(
    data: dict,
    expires_minutes: int | None = None
) -> str:

    to_encode = data.copy()

    if expires_minutes is None:
        expires_minutes = settings.jwt_access_token_expire_minutes

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise credentials_exception

    return user

def require_role(required_role: str):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker
from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request
from jwt import InvalidTokenError
from sqlmodel import Session

from .config import settings
from .database import get_db
from .models import User


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except InvalidTokenError:
        return None
    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id.isdecimal():
        return None
    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        return None
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user_optional(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_roles(*roles):
    def _dependency(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return _dependency

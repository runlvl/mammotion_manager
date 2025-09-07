"""Authentication router for login/logout functionality."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import get_settings
from ..services.auth_service import AuthService
from ..core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


def get_auth_service() -> AuthService:
    """Get auth service instance."""
    return AuthService()


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page."""
    # Check if already logged in
    if request.session.get("authenticated"):
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Handle login form submission."""
    try:
        logger.info(f"Login attempt for user: {email}")
        
        # Validate input
        if not email or not password:
            raise AuthenticationError("Email and password are required")
        
        # Authenticate user with timeout handling
        try:
            user_data = await auth_service.authenticate(email, password)
        except Exception as auth_error:
            logger.error(f"Authentication service error: {str(auth_error)}")
            raise AuthenticationError(str(auth_error))
        
        # Store in session
        request.session["authenticated"] = True
        request.session["user_email"] = email
        request.session["user_data"] = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "account_type": user_data.get("account_type"),
            "country_code": user_data.get("country_code"),
            "cloud_token": user_data.get("cloud_token"),
            "preferences": user_data.get("preferences", {}),
            "last_login": user_data.get("last_login"),
            "created_at": user_data.get("created_at")
        }
        
        logger.info(f"User {email} logged in successfully")
        return RedirectResponse(url="/dashboard", status_code=302)
        
    except AuthenticationError as e:
        logger.warning(f"Login failed for {email}: {e.message}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": e.message,
                "email": email
            },
            status_code=400
        )
    except Exception as e:
        logger.error(f"Unexpected login error for {email}: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
                "email": email
            },
            status_code=500
        )


@router.get("/logout")
async def logout(request: Request):
    """Handle logout."""
    email = request.session.get("user_email", "unknown")
    
    # Clean up session resources if available
    user_data = request.session.get("user_data", {})
    if user_data:
        try:
            auth_service = AuthService()
            await auth_service.cleanup_session(user_data)
        except Exception as e:
            logger.warning(f"Error cleaning up session for {email}: {str(e)}")
    
    request.session.clear()
    logger.info(f"User {email} logged out")
    return RedirectResponse(url="/", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Display main dashboard."""
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/", status_code=302)
    
    user_email = request.session.get("user_email", "Unknown")
    user_data = request.session.get("user_data", {})
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user_email": user_email,
            "user_data": user_data
        }
    )

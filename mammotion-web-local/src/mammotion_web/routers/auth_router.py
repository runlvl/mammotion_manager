"""Authentication router."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)
router = APIRouter()


def get_templates(request: Request) -> Jinja2Templates:
    """Get templates from app state."""
    return request.app.state.templates


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Display login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "Mammotion Login"}
    )


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    templates: Jinja2Templates = Depends(get_templates)
):
    """Handle login form submission."""
    logger.info(f"Login attempt for email: {email}")
    
    try:
        # TODO: Implement real Mammotion authentication
        # For now, accept any non-empty credentials
        if email and password:
            logger.info(f"Login successful for: {email}")
            # Redirect to dashboard
            response = RedirectResponse(url="/dashboard", status_code=302)
            response.set_cookie(key="session", value=f"user_{email}", httponly=True)
            return response
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "title": "Mammotion Login",
                "error": "Login failed. Please check your credentials."
            }
        )


@router.get("/logout")
async def logout():
    """Handle logout."""
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key="session")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Display dashboard page."""
    # Check if user is logged in
    session = request.cookies.get("session")
    if not session:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Mammotion Dashboard",
            "user": session.replace("user_", "")
        }
    )

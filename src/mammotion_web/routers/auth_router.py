"""Authentication router for Mammotion Web."""

from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/auth", tags=["authentication"])

# Templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle login form submission with real Mammotion API authentication."""
    # Import here to avoid circular dependencies
    from ..services.mammotion_service import MammotionService
    
    try:
        # Create mammotion service and attempt real authentication
        mammotion_service = MammotionService()
        
        # Attempt login with real Mammotion API
        success = await mammotion_service.login(username, password)
        
        if success:
            request.session["authenticated"] = True
            request.session["username"] = username
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Mammotion credentials"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/logout")
async def logout(request: Request):
    """Handle logout."""
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

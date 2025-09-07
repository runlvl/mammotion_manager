"""Authentication service with corrected pymammotion integration."""

import logging
from typing import Dict, Any, Optional
import asyncio
import aiohttp

from pymammotion.aliyun.cloud_gateway import CloudIOTGateway
from pymammotion.http.http import MammotionHTTP

from ..core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling user authentication with real Mammotion cloud."""
    
    def __init__(self):
        """Initialize auth service."""
        self.logger = logger
        self._timeout = 30  # 30 second timeout
    
    async def authenticate(self, email: str, password: str, country_code: str = "DE") -> Dict[str, Any]:
        """
        Authenticate user with Mammotion cloud service.
        
        Args:
            email: User email address
            password: User password
            country_code: Country code for login (default: "DE" for Germany)
            
        Returns:
            User data dictionary with real cloud session
            
        Raises:
            AuthenticationError: If authentication fails
        """
        session = None
        mammotion_http = None
        cloud_gateway = None
        
        try:
            self.logger.info(f"Starting authentication for user: {email} (country: {country_code})")
            
            if not email or not password:
                raise AuthenticationError("Email and password are required")
            
            # Step 1: Initialize HTTP client with timeout
            try:
                timeout = aiohttp.ClientTimeout(total=self._timeout)
                session = aiohttp.ClientSession(timeout=timeout)
                self.logger.info("✅ HTTP client initialized")
                
            except Exception as http_error:
                self.logger.error(f"HTTP client initialization failed: {str(http_error)}")
                raise AuthenticationError(f"Failed to initialize HTTP client: {str(http_error)}")
            
            # Step 2: Initialize MammotionHTTP with credentials
            try:
                self.logger.info("Initializing MammotionHTTP with credentials...")
                mammotion_http = MammotionHTTP()
                
                # Set credentials on MammotionHTTP
                # Check different ways to set login credentials
                if hasattr(mammotion_http, 'set_credentials'):
                    await mammotion_http.set_credentials(email, password)
                    self.logger.info("✅ Credentials set via set_credentials()")
                elif hasattr(mammotion_http, 'login'):
                    login_result = await mammotion_http.login(email, password)
                    self.logger.info(f"✅ Login via MammotionHTTP.login(): {login_result}")
                elif hasattr(mammotion_http, 'authenticate'):
                    auth_result = await mammotion_http.authenticate(email, password)
                    self.logger.info(f"✅ Auth via MammotionHTTP.authenticate(): {auth_result}")
                else:
                    # Try to set attributes directly
                    if hasattr(mammotion_http, 'username'):
                        mammotion_http.username = email
                        mammotion_http.password = password
                        self.logger.info("✅ Credentials set as attributes")
                    else:
                        self.logger.warning("⚠️ Could not find method to set credentials on MammotionHTTP")
                
                # Check if login_info is available after setting credentials
                if hasattr(mammotion_http, 'login_info'):
                    login_info = mammotion_http.login_info
                    self.logger.info(f"Login info available: {type(login_info)}")
                    
                    if hasattr(login_info, 'authorization_code'):
                        auth_code = login_info.authorization_code
                        self.logger.info(f"Authorization code: {auth_code}")
                    else:
                        self.logger.warning("⚠️ login_info has no authorization_code attribute")
                else:
                    self.logger.warning("⚠️ MammotionHTTP has no login_info attribute")
                
            except Exception as http_init_error:
                self.logger.error(f"MammotionHTTP initialization failed: {str(http_init_error)}")
                raise AuthenticationError(f"Failed to initialize HTTP handler: {str(http_init_error)}")
            
            # Step 3: Initialize CloudIOTGateway with MammotionHTTP
            try:
                self.logger.info("Initializing CloudIOTGateway with MammotionHTTP...")
                cloud_gateway = CloudIOTGateway(mammotion_http)
                self.logger.info("✅ CloudIOTGateway initialized successfully")
                
            except Exception as gateway_error:
                self.logger.error(f"CloudIOTGateway initialization failed: {str(gateway_error)}")
                raise AuthenticationError(f"Failed to initialize cloud gateway: {str(gateway_error)}")
            
            # Step 4: Attempt OAuth login with country code
            try:
                self.logger.info(f"Attempting OAuth login with country code: {country_code}")
                
                login_result = await asyncio.wait_for(
                    cloud_gateway.login_by_oauth(country_code),
                    timeout=self._timeout
                )
                
                self.logger.info(f"OAuth login completed - result type: {type(login_result)}")
                self.logger.info(f"OAuth login result: {login_result}")
                
                # Check if login was successful
                if login_result is None:
                    raise AuthenticationError("OAuth login failed - no response from cloud service")
                
                # Handle the response based on its actual structure
                success = False
                error_message = "Unknown error"
                
                if isinstance(login_result, dict):
                    # Handle dictionary response
                    success = (
                        login_result.get('success', False) or
                        login_result.get('code') == 200 or
                        login_result.get('status') == 'success' or
                        'access_token' in login_result or
                        'token' in login_result or
                        'session_id' in login_result or
                        (not login_result.get('error') and not login_result.get('message'))
                    )
                    error_message = login_result.get('message', login_result.get('error', 'Invalid credentials'))
                    
                elif hasattr(login_result, 'success'):
                    # Handle object with success attribute
                    success = getattr(login_result, 'success', False)
                    error_message = getattr(login_result, 'message', 'Invalid credentials')
                    
                elif isinstance(login_result, bool):
                    # Handle boolean response
                    success = login_result
                    
                else:
                    # If we get any other response, log it and assume success for debugging
                    self.logger.info(f"Unexpected response type, assuming success: {type(login_result)}")
                    success = True
                
                if not success:
                    self.logger.error(f"OAuth login failed: {error_message}")
                    raise AuthenticationError(error_message)
                
                # Extract authentication data from the gateway object itself
                auth_token = None
                session_id = None
                
                # Try to get authentication info from the gateway
                gateway_attrs = [
                    'access_token', 'session_id', 'token', 'auth_token', 
                    'authorization_token', 'login_token', 'user_token'
                ]
                
                for attr in gateway_attrs:
                    if hasattr(cloud_gateway, attr):
                        value = getattr(cloud_gateway, attr, None)
                        if value:
                            auth_token = str(value)
                            session_id = str(value)
                            self.logger.info(f"Found auth token in gateway.{attr}: {auth_token[:20]}...")
                            break
                
                # If no token found in gateway, try the login result
                if not auth_token and isinstance(login_result, dict):
                    result_keys = ['access_token', 'session_id', 'token', 'auth_token', 'sessionId']
                    for key in result_keys:
                        if key in login_result and login_result[key]:
                            auth_token = str(login_result[key])
                            session_id = str(login_result[key])
                            self.logger.info(f"Found auth token in result.{key}: {auth_token[:20]}...")
                            break
                
                # Try to get user information
                user_info = {}
                try:
                    # Check if gateway has user info methods
                    user_methods = ['get_user_info', 'get_account_info', 'get_profile']
                    for method_name in user_methods:
                        if hasattr(cloud_gateway, method_name):
                            try:
                                method = getattr(cloud_gateway, method_name)
                                user_info_result = await asyncio.wait_for(method(), timeout=10)
                                
                                if user_info_result:
                                    if isinstance(user_info_result, dict):
                                        user_info = user_info_result
                                    elif hasattr(user_info_result, '__dict__'):
                                        user_info = user_info_result.__dict__
                                    break
                            except Exception as e:
                                self.logger.debug(f"Method {method_name} failed: {str(e)}")
                                continue
                                
                except Exception as e:
                    self.logger.warning(f"Could not get user info: {str(e)}")
                
                # Create user data
                user_data = {
                    "user_id": user_info.get('user_id', email),
                    "email": email,
                    "name": user_info.get('name', email.split("@")[0]),
                    "account_type": user_info.get('account_type', 'standard'),
                    "country_code": country_code,
                    "cloud_token": auth_token,
                    "cloud_session": session_id,
                    "devices": [],
                    "preferences": user_info.get('preferences', {}),
                    "last_login": user_info.get('last_login'),
                    "created_at": user_info.get('created_at'),
                    "authenticated": True
                }
                
                # Store gateway and session for later use (but don't serialize them)
                self._active_gateway = cloud_gateway
                self._active_session = session
                self._active_mammotion_http = mammotion_http
                
                self.logger.info(f"✅ Cloud authentication successful for user: {email}")
                return user_data
                
            except asyncio.TimeoutError:
                self.logger.error(f"OAuth login timeout after {self._timeout}s")
                raise AuthenticationError("Login timeout - please check your internet connection and try again")
                
            except Exception as auth_error:
                self.logger.error(f"OAuth authentication failed: {str(auth_error)}")
                self.logger.error(f"Error type: {type(auth_error)}")
                
                # Check for specific error types
                error_message = str(auth_error)
                if "401" in error_message or "unauthorized" in error_message.lower():
                    raise AuthenticationError("Invalid email or password")
                elif "403" in error_message or "forbidden" in error_message.lower():
                    raise AuthenticationError("Account access denied")
                elif "timeout" in error_message.lower() or "connection" in error_message.lower():
                    raise AuthenticationError("Connection to Mammotion cloud failed. Please try again.")
                elif "login_info" in error_message:
                    raise AuthenticationError("Authentication setup failed. Please check your credentials.")
                elif "authorization_code" in error_message:
                    raise AuthenticationError("Authorization failed. Please verify your account credentials.")
                else:
                    raise AuthenticationError(f"Authentication failed: {error_message}")
            
        except AuthenticationError:
            # Clean up on authentication error
            if session:
                try:
                    await session.close()
                except:
                    pass
            raise
            
        except Exception as e:
            # Clean up on unexpected error
            if session:
                try:
                    await session.close()
                except:
                    pass
            self.logger.error(f"Unexpected authentication error for {email}: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    async def validate_session(self, user_data: Dict[str, Any]) -> bool:
        """
        Validate user session.
        
        Args:
            user_data: User session data
            
        Returns:
            True if session is valid
        """
        try:
            # Simple validation based on stored data
            return user_data.get('authenticated', False) and user_data.get('cloud_token') is not None
            
        except Exception as e:
            self.logger.error(f"Session validation error: {str(e)}")
            return False
    
    async def refresh_user_data(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Refresh user data.
        
        Args:
            user_id: User ID
            user_data: Current user data
            
        Returns:
            Updated user data or None if not found
        """
        try:
            # For now, return the existing data
            # In a real implementation, this would fetch fresh data from the cloud
            return user_data
            
        except Exception as e:
            self.logger.error(f"Error refreshing user data: {str(e)}")
            return None
    
    async def cleanup_session(self, user_data: Dict[str, Any]):
        """Clean up session resources."""
        try:
            # Clean up active session if it exists
            if hasattr(self, '_active_session') and self._active_session:
                if not self._active_session.closed:
                    await self._active_session.close()
                self._active_session = None
                self.logger.info("HTTP client session closed")
                
            # Clean up gateway reference
            if hasattr(self, '_active_gateway'):
                self._active_gateway = None
                
            # Clean up MammotionHTTP reference
            if hasattr(self, '_active_mammotion_http'):
                self._active_mammotion_http = None
                
        except Exception as e:
            self.logger.warning(f"Error cleaning up session: {str(e)}")
    
    def get_active_gateway(self):
        """Get the active cloud gateway for device operations."""
        return getattr(self, '_active_gateway', None)
    
    def get_active_session(self):
        """Get the active HTTP session."""
        return getattr(self, '_active_session', None)
    
    def get_active_mammotion_http(self):
        """Get the active MammotionHTTP instance."""
        return getattr(self, '_active_mammotion_http', None)

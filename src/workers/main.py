"""
OWASP BLT - Cloudflare Python Worker
Main API handler for dynamic features
"""

from js import Response, fetch, Headers
import json
from datetime import datetime

# ===================================
# Configuration
# ===================================
ALLOWED_ORIGINS = [
    'https://owasp-blt.github.io',
    'http://localhost:3000',
    'http://localhost:8000',
]

# ===================================
# CORS Helpers
# ===================================
def get_cors_headers(origin):
    """Generate CORS headers for the response"""
    if origin in ALLOWED_ORIGINS or origin.endswith('.github.io'):
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400',
        }
    return {}

def create_response(data, status=200, origin=None):
    """Create a JSON response with CORS headers"""
    headers = {
        'Content-Type': 'application/json',
        **get_cors_headers(origin) if origin else {},
    }
    
    return Response.new(
        json.dumps(data),
        status=status,
        headers=Headers.new(headers)
    )

def handle_cors_preflight(origin):
    """Handle CORS preflight requests"""
    return Response.new(
        '',
        status=204,
        headers=Headers.new(get_cors_headers(origin))
    )

# ===================================
# Route Handlers
# ===================================

async def handle_stats(request):
    """Handle /api/stats endpoint"""
    # In production, this would fetch from a database
    # For now, return mock data
    stats = {
        'bugs_reported': 15234,
        'active_researchers': 3421,
        'rewards_distributed': '$248,500',
        'projects_protected': 892,
    }
    
    return create_response(stats, origin=request.headers.get('Origin'))

async def handle_auth_login(request):
    """Handle /api/auth/login endpoint"""
    try:
        body = await request.json()
        email = body.get('email')
        password = body.get('password')
        
        # IMPORTANT: This is mock authentication for development/demo only
        # TODO: In production, implement proper authentication:
        # 1. Query database for user by email
        # 2. Verify password hash using bcrypt or argon2
        # 3. Generate proper JWT token with secure secret
        # 4. Set appropriate token expiration
        # 5. Implement refresh token mechanism
        
        # Mock authentication - DO NOT USE IN PRODUCTION
        if email and password:
            user = {
                'id': 1,
                'username': email.split('@')[0],
                'email': email,
            }
            
            # WARNING: This is a mock token - NOT SECURE for production
            # Replace with proper JWT library (e.g., PyJWT)
            # Example: token = jwt.encode({'user_id': user['id']}, JWT_SECRET, algorithm='HS256')
            import hashlib
            token = f"mock_{hashlib.sha256(f'{email}{datetime.now().isoformat()}'.encode()).hexdigest()}"
            
            return create_response({
                'success': True,
                'token': token,
                'user': user,
            }, origin=request.headers.get('Origin'))
        
        return create_response({
            'success': False,
            'error': 'Invalid credentials'
        }, status=401, origin=request.headers.get('Origin'))
        
    except Exception as e:
        return create_response({
            'success': False,
            'error': str(e)
        }, status=400, origin=request.headers.get('Origin'))

async def handle_auth_signup(request):
    """Handle /api/auth/signup endpoint"""
    try:
        body = await request.json()
        username = body.get('username')
        email = body.get('email')
        password = body.get('password')
        
        # IMPORTANT: This is mock signup for development/demo only
        # TODO: In production, implement proper user registration:
        # 1. Validate input (email format, password strength, username uniqueness)
        # 2. Hash password with bcrypt/argon2 before storing
        # 3. Check for existing user in database
        # 4. Store user securely in database
        # 5. Send verification email
        # 6. Generate secure JWT token
        
        # Mock signup - DO NOT USE IN PRODUCTION
        if username and email and password:
            user = {
                'id': 1,
                'username': username,
                'email': email,
            }
            
            # WARNING: Mock token - NOT SECURE for production
            import hashlib
            token = f"mock_{hashlib.sha256(f'{email}{datetime.now().isoformat()}'.encode()).hexdigest()}"
            
            return create_response({
                'success': True,
                'token': token,
                'user': user,
            }, origin=request.headers.get('Origin'))
        
        return create_response({
            'success': False,
            'error': 'Invalid signup data'
        }, status=400, origin=request.headers.get('Origin'))
        
    except Exception as e:
        return create_response({
            'success': False,
            'error': str(e)
        }, status=400, origin=request.headers.get('Origin'))

async def handle_auth_me(request):
    """Handle /api/auth/me endpoint"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return create_response({
            'error': 'Unauthorized'
        }, status=401, origin=request.headers.get('Origin'))
    
    token = auth_header.replace('Bearer ', '')
    
    # IMPORTANT: This is mock token validation for development/demo only
    # TODO: In production, implement proper JWT validation:
    # 1. Verify JWT signature with secret key
    # 2. Check token expiration
    # 3. Validate token claims
    # 4. Query database for current user data
    # Example: decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    
    # Mock token validation - DO NOT USE IN PRODUCTION
    if token.startswith('mock_'):
        # Extract email from mock token (this is insecure)
        # In production, decode JWT properly
        try:
            # For demo purposes, return a mock user
            user = {
                'id': 1,
                'username': 'demo_user',
                'email': 'demo@example.com',
            }
            return create_response({
                'user': user
            }, origin=request.headers.get('Origin'))
        except Exception:
            pass
    
    return create_response({
        'error': 'Invalid token'
    }, status=401, origin=request.headers.get('Origin'))

async def handle_auth_logout(request):
    """Handle /api/auth/logout endpoint"""
    # In production, invalidate token in database
    return create_response({
        'success': True
    }, origin=request.headers.get('Origin'))

async def handle_bugs_list(request):
    """Handle /api/bugs endpoint"""
    # In production, fetch from database with pagination
    bugs = [
        {
            'id': 1,
            'title': 'SQL Injection in login form',
            'severity': 'critical',
            'status': 'open',
            'reporter': 'alice',
            'reward': 500,
        },
        {
            'id': 2,
            'title': 'XSS vulnerability in comments',
            'severity': 'high',
            'status': 'verified',
            'reporter': 'bob',
            'reward': 300,
        },
    ]
    
    return create_response({
        'bugs': bugs,
        'total': len(bugs),
    }, origin=request.headers.get('Origin'))

async def handle_leaderboard(request):
    """Handle /api/leaderboard endpoint"""
    # In production, fetch from database
    leaderboard = [
        {'rank': 1, 'username': 'alice', 'points': 2500, 'bugs': 45},
        {'rank': 2, 'username': 'bob', 'points': 2100, 'bugs': 38},
        {'rank': 3, 'username': 'charlie', 'points': 1800, 'bugs': 32},
    ]
    
    return create_response({
        'leaderboard': leaderboard
    }, origin=request.headers.get('Origin'))

# ===================================
# Router
# ===================================

ROUTES = {
    'GET': {
        '/api/stats': handle_stats,
        '/api/auth/me': handle_auth_me,
        '/api/bugs': handle_bugs_list,
        '/api/leaderboard': handle_leaderboard,
    },
    'POST': {
        '/api/auth/login': handle_auth_login,
        '/api/auth/signup': handle_auth_signup,
        '/api/auth/logout': handle_auth_logout,
    },
}

async def route_request(request):
    """Route the request to the appropriate handler"""
    method = request.method
    url = request.url
    
    # Parse URL properly to extract path
    # Handle both full URLs (https://api.example.com/api/stats) and paths (/api/stats)
    if url.startswith('http://') or url.startswith('https://'):
        # Extract path from full URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path
    else:
        # Already a path
        path = url.split('?')[0]  # Remove query params
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return handle_cors_preflight(request.headers.get('Origin'))
    
    # Find and execute handler
    method_routes = ROUTES.get(method, {})
    handler = method_routes.get(path)
    
    if handler:
        return await handler(request)
    
    # 404 Not Found
    return create_response({
        'error': 'Not found'
    }, status=404, origin=request.headers.get('Origin'))

# ===================================
# Main Entry Point
# ===================================

async def on_fetch(request):
    """Main entry point for Cloudflare Worker"""
    try:
        return await route_request(request)
    except Exception as e:
        return create_response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500, origin=request.headers.get('Origin'))

from js import Response, Headers, URL, console
import json
import hashlib
import hmac
import base64
import traceback
from datetime import datetime, timedelta

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
    if not origin:
        return {}
        
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
    js_headers = Headers.new()
    js_headers.set('Content-Type', 'application/json')
    
    cors = get_cors_headers(origin)
    for k, v in cors.items():
        js_headers.set(k, v)
    
    return Response.new(
        json.dumps(data),
        status=status,
        headers=js_headers
    )

def handle_html_response(html, origin=None):
    """Create an HTML response with CORS headers"""
    js_headers = Headers.new()
    js_headers.set('Content-Type', 'text/html')
    js_headers.set('Access-Control-Allow-Origin', '*')
    
    return Response.new(
        html,
        status=200,
        headers=js_headers
    )

def handle_cors_preflight(origin):
    """Handle CORS preflight requests"""
    return Response.new(
        '',
        status=204,
        headers=Headers.new(get_cors_headers(origin))
    )

# ===================================
# Security Helpers
# ===================================

JWT_SECRET = "dev-secret-key" # In production, set this via wrangler secret put

def hash_password(password, salt=None):
    """Hash a password using PBKDF2"""
    if salt is None:
        import random
        salt = "".join([random.choice("0123456789abcdef") for _ in range(16)])
    
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{dk.hex()}"

def verify_password(stored_password, provided_password):
    """Verify a stored password hash against a provided password"""
    try:
        if ':' in stored_password:
            salt, hash_val = stored_password.split(':')
            dk = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt.encode(), 100000)
            return dk.hex() == hash_val
        return hashlib.sha256(provided_password.encode()).hexdigest() == stored_password
    except Exception:
        return False

def generate_jwt(payload, secret):
    """Generate a simple JWT token (HS256)"""
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, separators=(',', ':'))
    header_b64 = base64.urlsafe_b64encode(header_json.encode()).decode().rstrip('=')
    
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')
    
    signature_input = f"{header_b64}.{payload_b64}"
    sig = hmac.new(secret.encode(), signature_input.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip('=')
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_jwt(token, secret):
    """Verify a JWT token and return the payload"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        signature_input = f"{header_b64}.{payload_b64}"
        sig = hmac.new(secret.encode(), signature_input.encode(), hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip('=')
        
        if signature_b64 != expected_sig_b64:
            return None
        
        padding = '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode()
        payload = json.loads(payload_json)
        
        if 'exp' in payload and datetime.now().timestamp() > payload['exp']:
            return None
            
        return payload
    except Exception:
        return None

# ===================================
# Route Handlers
# ===================================

async def handle_stats(request, env=None):
    """Handle /api/stats endpoint"""
    if not env or not hasattr(env, 'DB'):
        return create_response({'error': 'Database binding missing'}, status=500, origin=request.headers.get('Origin'))

    try:
        results = await env.DB.prepare("SELECT key, value FROM stats").all()
        stats = {row.key: row.value for row in results.results}
        
        if not stats:
            return create_response({'error': 'No stats found'}, status=404, origin=request.headers.get('Origin'))

        html = f"""
        <div class="stat-card">
            <div class="stat-value">{stats.get('bugs_reported', 0)}</div>
            <div class="stat-label">Bugs Reported</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.get('active_researchers', 0)}</div>
            <div class="stat-label">Active Researchers</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.get('rewards_distributed', '$0')}</div>
            <div class="stat-label">Rewards Distributed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.get('projects_protected', 0)}</div>
            <div class="stat-label">Projects Protected</div>
        </div>
        """
        return handle_html_response(html, origin=request.headers.get('Origin'))
    except Exception as e:
        print(f"D1 Query Error: {e}")
        return create_response({'error': str(e)}, status=500, origin=request.headers.get('Origin'))

async def handle_auth_login(request, env=None):
    """Handle /api/auth/login endpoint"""
    if not env or not hasattr(env, 'DB'):
        return create_response({'error': 'Database binding missing'}, status=500, origin=request.headers.get('Origin'))

    try:
        body = await request.json()
        # Direct property access for JS objects
        email = body.email
        password = body.password
        
        if not email or not password:
            return create_response({'success': False, 'error': 'Missing credentials'}, status=400, origin=request.headers.get('Origin'))

        result = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first()
        
        if result and verify_password(result.password_hash, password):
            user = {
                'id': result.id,
                'username': result.username,
                'email': result.email,
            }
            
            secret = getattr(env, 'JWT_SECRET', JWT_SECRET)
            payload = {
                'sub': result.id,
                'username': result.username,
                'exp': (datetime.now() + timedelta(days=7)).timestamp()
            }
            token = generate_jwt(payload, secret)
            
            await env.DB.prepare("UPDATE users SET last_login = ? WHERE id = ?").bind(datetime.now().isoformat(), result.id).run()
            
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
        err_info = traceback.format_exc()
        console.log(f"Login Error: {err_info}")
        return create_response({
            'success': False,
            'error': str(e),
            'traceback': err_info
        }, status=400, origin=request.headers.get('Origin'))

async def handle_auth_signup(request, env=None):
    """Handle /api/auth/signup endpoint"""
    if not env or not hasattr(env, 'DB'):
        return create_response({'error': 'Database binding missing'}, status=500, origin=request.headers.get('Origin'))

    try:
        body = await request.json()
        # Direct property access for JS objects
        username = body.username
        email = body.email
        password = body.password
        
        if not username or not email or not password:
            return create_response({'success': False, 'error': 'Invalid signup data'}, status=400, origin=request.headers.get('Origin'))

        existing = await env.DB.prepare("SELECT id FROM users WHERE email = ? OR username = ?").bind(email, username).first()
        if existing:
            return create_response({'success': False, 'error': 'User already exists'}, status=400, origin=request.headers.get('Origin'))

        hashed_pw = hash_password(password)
        await env.DB.prepare(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)"
        ).bind(username, email, hashed_pw).run()

        new_user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first()
        
        user = {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
        }
        
        secret = getattr(env, 'JWT_SECRET', JWT_SECRET)
        payload = {
            'sub': new_user.id,
            'username': new_user.username,
            'exp': (datetime.now() + timedelta(days=7)).timestamp()
        }
        token = generate_jwt(payload, secret)
        
        return create_response({
            'success': True,
            'token': token,
            'user': user,
        }, origin=request.headers.get('Origin'))
        
    except Exception as e:
        err_info = traceback.format_exc()
        console.log(f"Signup Error: {err_info}")
        return create_response({
            'success': False,
            'error': str(e),
            'traceback': err_info
        }, status=400, origin=request.headers.get('Origin'))

async def handle_auth_me(request, env=None):
    """Handle /api/auth/me endpoint"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return create_response({
            'error': 'Unauthorized'
        }, status=401, origin=request.headers.get('Origin'))
    
    token = auth_header.replace('Bearer ', '')
    secret = getattr(env, 'JWT_SECRET', JWT_SECRET)
    
    payload = verify_jwt(token, secret)
    if payload and 'sub' in payload:
        try:
            result = await env.DB.prepare("SELECT id, username, email FROM users WHERE id = ?").bind(payload['sub']).first()
            if result:
                user = {
                    'id': result.id,
                    'username': result.username,
                    'email': result.email,
                }
                return create_response({
                    'user': user
                }, origin=request.headers.get('Origin'))
        except Exception:
            pass
    
    return create_response({
        'error': 'Invalid token'
    }, status=401, origin=request.headers.get('Origin'))

async def handle_auth_logout(request, env=None):
    """Handle /api/auth/logout endpoint"""
    return create_response({
        'success': True
    }, origin=request.headers.get('Origin'))

async def handle_bugs_list(request, env=None):
    """Handle /api/bugs endpoint (GET and POST)"""
    if not env or not hasattr(env, 'DB'):
        return create_response({'error': 'Database binding missing'}, status=500, origin=request.headers.get('Origin'))

    if request.method == 'POST':
        try:
            body = await request.json()
            title = body.title
            description = body.description
            severity = body.severity
            
            await env.DB.prepare(
                "INSERT INTO bugs (title, description, severity, status) VALUES (?, ?, ?, ?)"
            ).bind(title, description, severity, 'open').run()

            html = """
                <div style="background: #ecfdf5; color: #065f46; padding: 2rem; border-radius: 0.5rem; text-align: center; border: 1px solid #10b981;">
                    <h2 style="margin-bottom: 1rem;">✅ Report Submitted!</h2>
                    <p>Thank you for contributing to OWASP BLT. Our team will review your report shortly.</p>
                    <a href="/" class="btn btn-primary" style="margin-top: 1.5rem; display: inline-block;">Back to Home</a>
                </div>
            """
            return handle_html_response(html, origin=request.headers.get('Origin'))
        except Exception as e:
            return create_response({'error': str(e)}, status=500, origin=request.headers.get('Origin'))

    try:
        results = await env.DB.prepare("SELECT * FROM bugs ORDER BY created_at DESC LIMIT 20").all()
        return create_response({'bugs': results.results}, origin=request.headers.get('Origin'))
    except Exception as e:
        return create_response({'error': str(e)}, status=500, origin=request.headers.get('Origin'))

async def handle_leaderboard(request, env=None):
    """Handle /api/leaderboard endpoint"""
    if not env or not hasattr(env, 'DB'):
        return create_response({'error': 'Database binding missing'}, status=500, origin=request.headers.get('Origin'))

    try:
        results = await env.DB.prepare(
            '''SELECT rank, ('User #' || user_id) AS username, points, bugs_verified AS bugs
            FROM leaderboard
            ORDER BY points DESC
            LIMIT 10''').all()
        leaderboard = results.results
        
        rows = "".join([
            f"""
            <div class="leaderboard-row">
                <div class="rank">{item.rank}</div>
                <div class="username">{item.username}</div>
                <div class="stat">{item.points} pts</div>
                <div class="stat">{item.bugs} bugs</div>
            </div>
            """ for item in leaderboard
        ])
        
        html = f"""
        <div class="leaderboard-table">
            <div class="leaderboard-row leaderboard-header">
                <div>Rank</div>
                <div>Researcher</div>
                <div style="text-align: right;">Points</div>
                <div style="text-align: right;">Bugs</div>
            </div>
            {rows}
        </div>
        """
        return handle_html_response(html, origin=request.headers.get('Origin'))
    except Exception as e:
        return create_response({'error': str(e)}, status=500, origin=request.headers.get('Origin'))

async def handle_projects(request, env=None):
    """Handle /api/projects endpoint"""
    if not env or not hasattr(env, 'DB'):
        return create_response({'error': 'Database binding missing'}, status=500, origin=request.headers.get('Origin'))

    try:
        results = await env.DB.prepare("SELECT * FROM projects").all()
        projects = results.results
        
        cards = "".join([
            f"""
            <div class="project-card">
                <div class="project-header">
                    <div class="project-logo">🛡️</div>
                    <div class="project-info">
                        <div class="project-name">{p.name}</div>
                        <div class="project-type">{p.type}</div>
                    </div>
                </div>
                <div class="project-reward">{getattr(p, 'reward', 'N/A')}</div>
                <div class="project-stats">
                    <div class="stat">
                        <div class="stat-value">{getattr(p, 'bugs', 0)}</div>
                        <div class="stat-label">Bugs</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">Active</div>
                        <div class="stat-label">Status</div>
                    </div>
                </div>
            </div>
            """ for p in projects
        ])
        return handle_html_response(cards, origin=request.headers.get('Origin'))
    except Exception as e:
        return create_response({'error': str(e)}, status=500, origin=request.headers.get('Origin'))

# ===================================
# Router
# ===================================

ROUTES = {
    'GET': {
        '/api/stats': handle_stats,
        '/api/auth/me': handle_auth_me,
        '/api/bugs': handle_bugs_list,
        '/api/leaderboard': handle_leaderboard,
        '/api/projects': handle_projects,
    },
    'POST': {
        '/api/auth/login': handle_auth_login,
        '/api/auth/signup': handle_auth_signup,
        '/api/auth/logout': handle_auth_logout,
        '/api/bugs': handle_bugs_list,
    },
}

async def route_request(request, env):
    """Route the request to the appropriate handler"""
    url = URL.new(request.url)
    path = url.pathname
    
    if request.method == 'OPTIONS':
        return handle_cors_preflight(request.headers.get('Origin'))
    
    handler = ROUTES.get(request.method, {}).get(path)
    if handler:
        try:
            return await handler(request, env)
        except Exception as e:
            err_info = traceback.format_exc()
            console.log(f"Handler Error: {err_info}")
            raise e
    
    if hasattr(env, 'ASSETS'):
        try:
            fetch_url = request.url
            if path == '/':
                fetch_url = str(url).replace(path, '/index.html')
            return await env.ASSETS.fetch(fetch_url)
        except Exception as e:
            console.log(f"Assets Error: {str(e)}")
    
    return create_response({'error': 'Not found', 'path': path}, status=404, origin=request.headers.get('Origin'))

# ===================================
# Main Entry Point
# ===================================

async def on_fetch(request, env):
    """Main entry point for Cloudflare Worker"""
    try:
        return await route_request(request, env)
    except Exception as e:
        err_info = traceback.format_exc()
        return create_response({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': err_info
        }, status=500, origin=request.headers.get('Origin'))

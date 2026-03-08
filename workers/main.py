from js import Response, Headers, URL, console
import json
import hashlib
import hmac
import base64
import traceback
import secrets
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
        salt = secrets.token_hex(8)
    
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
        
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
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
            'error': str(e)
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
            'error': str(e)
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
        # Auth check for bug reporting
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return create_response({'error': 'Authentication required to report bugs'}, status=401, origin=request.headers.get('Origin'))
        
        token = auth_header.replace('Bearer ', '')
        secret = getattr(env, 'JWT_SECRET', JWT_SECRET)
        payload = verify_jwt(token, secret)
        
        if not payload or 'sub' not in payload:
            return create_response({'error': 'Invalid or expired session'}, status=401, origin=request.headers.get('Origin'))
            
        try:
            reporter_id = int(payload['sub'])
            body = await request.json()
            title = body.title
            description = body.description
            severity = getattr(body, 'severity', 'medium')
            url_val = getattr(body, 'url', None)
            bug_type = getattr(body, 'type', 'other')
            steps = getattr(body, 'steps', None)
            
            await env.DB.prepare(
                "INSERT INTO bugs (title, description, severity, status, url, bug_type, steps_to_reproduce, reporter_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            ).bind(title, description, severity, 'open', url_val, bug_type, steps, reporter_id).run()

            # For HTMX submission
            html = """
                <div style="background: #ecfdf5; color: #065f46; padding: 2rem; border-radius: 0.5rem; text-align: center; border: 1px solid #10b981;">
                    <h2 style="margin-bottom: 1rem;">✅ Report Submitted!</h2>
                    <p>Thank you for contributing to OWASP BLT. Our team will review your report shortly.</p>
                    <a href="/pages/dashboard.html" class="btn btn-primary" style="margin-top: 1.5rem; display: inline-block;">Go to Dashboard</a>
                </div>
            """
            return handle_html_response(html, origin=request.headers.get('Origin'))
        except Exception as e:
            return create_response({'error': 'Failed to process request'}, status=500, origin=request.headers.get('Origin'))

    # GET case (list all bugs)
    try:
        results = await env.DB.prepare("SELECT * FROM bugs ORDER BY created_at DESC LIMIT 20").all()
        # Convert results to plain dicts to avoid JsProxy serialization errors
        bugs_list = []
        if results.results:
            for b in results.results:
                bugs_list.append({
                    'id': getattr(b, 'id', None),
                    'title': getattr(b, 'title', 'Untitled'),
                    'description': getattr(b, 'description', ''),
                    'severity': getattr(b, 'severity', 'medium'),
                    'status': getattr(b, 'status', 'open'),
                    'created_at': getattr(b, 'created_at', '')
                })
        return create_response({'bugs': bugs_list}, origin=request.headers.get('Origin'))
    except Exception as e:
        return create_response({'error': str(e)}, status=500, origin=request.headers.get('Origin'))

async def handle_user_bugs(request, env=None):
    """Handle /api/user/bugs endpoint - Fetch bugs for current user"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return create_response({'error': 'Unauthorized'}, status=401, origin=request.headers.get('Origin'))
        
    token = auth_header.replace('Bearer ', '')
    secret = getattr(env, 'JWT_SECRET', JWT_SECRET)
    payload = verify_jwt(token, secret)
    
    if not payload or 'sub' not in payload:
        return create_response({'error': 'Unauthorized'}, status=401, origin=request.headers.get('Origin'))
        
    try:
        reporter_id = int(payload['sub'])
        results = await env.DB.prepare("SELECT * FROM bugs WHERE reporter_id = ? ORDER BY created_at DESC").bind(reporter_id).all()
        
        # Return HTML rows for HTMX dashboard
        if "text/html" in request.headers.get("Accept", ""):
            if not results.results:
                return handle_html_response('<p class="text-gray-500 py-4">No reports found yet.</p>', origin=request.headers.get('Origin'))
                
            rows = "".join([
                f"""
                <tr class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors">
                    <td class="py-4 px-2 text-sm font-medium">{getattr(b, 'title', 'Untitled')}</td>
                    <td class="py-4 px-2 text-xs">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase 
                            {'bg-red-100 text-red-600' if b.severity == 'critical' else 
                             'bg-orange-100 text-orange-600' if b.severity == 'high' else 
                             'bg-yellow-100 text-yellow-600' if b.severity == 'medium' else 
                             'bg-green-100 text-green-600'}">
                            {b.severity}
                        </span>
                    </td>
                    <td class="py-4 px-2 text-xs">
                        <span class="px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 capitalize">
                            {b.status}
                        </span>
                    </td>
                    <td class="py-4 px-2 text-xs text-gray-400">{b.created_at[:10]}</td>
                </tr>
                """ for b in results.results
            ])
            return handle_html_response(rows, origin=request.headers.get('Origin'))
            
        # Convert results to plain dicts
        bugs_list = []
        if results.results:
            for b in results.results:
                bugs_list.append({
                    'id': getattr(b, 'id', None),
                    'title': getattr(b, 'title', 'Untitled'),
                    'status': getattr(b, 'status', 'open'),
                    'severity': getattr(b, 'severity', 'medium'),
                    'created_at': getattr(b, 'created_at', '')
                })
        return create_response({'bugs': bugs_list}, origin=request.headers.get('Origin'))
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
        '/api/user/bugs': handle_user_bugs,
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
        return create_response({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }, status=500, origin=request.headers.get('Origin'))

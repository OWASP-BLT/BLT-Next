# Contributing to BLT-Next

Thank you for your interest in contributing to BLT-Next! This guide will help you get started.

## Code of Conduct

By participating in this project, you agree to abide by the [OWASP Code of Conduct](https://owasp.org/www-policy/operational/code-of-conduct).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment details** (browser, OS, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear title** describing the enhancement
- **Provide detailed description** of the proposed functionality
- **Explain why** this enhancement would be useful
- **Include mockups** or examples if applicable

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## Development Setup

### Prerequisites

- Git
- Modern web browser
- Python 3.11+ (for worker development)
- Node.js 18+ (for Wrangler CLI)

### Local Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/BLT-Next.git
   cd BLT-Next
   ```

2. **Start local server:**
   ```bash
   python -m http.server 8000
   ```

3. **Open in browser:**
   ```
   http://localhost:8000
   ```

### Worker Development

1. **Install Wrangler:**
   ```bash
   npm install -g wrangler
   ```

2. **Develop locally:**
   ```bash
   cd src/workers
   wrangler dev
   ```

3. **Test endpoints:**
   ```bash
   curl http://localhost:8787/api/stats
   ```

## Coding Guidelines

### HTML

- Use **semantic HTML5** elements
- Ensure **accessibility** (ARIA labels, alt text, etc.)
- Follow **progressive enhancement** principles
- Keep markup **clean and readable**

Example:
```html
<section class="features" aria-label="Platform features">
    <h2 class="section-title">Features</h2>
    <!-- Content -->
</section>
```

### CSS

- Use **CSS variables** for theming
- Follow **BEM methodology** for class names
- Keep **specificity low**
- Write **mobile-first** responsive styles
- Avoid `!important` unless absolutely necessary

Example:
```css
.feature-card {
    padding: var(--spacing-lg);
    background: var(--color-white);
}

.feature-card__title {
    font-size: var(--font-size-xl);
}

.feature-card--highlighted {
    border: 2px solid var(--color-primary);
}
```

### JavaScript

- Use **ES6+** features
- Write **modular** code
- Add **JSDoc comments** for functions
- Handle **errors gracefully**
- Avoid dependencies where possible

Example:
```javascript
/**
 * Fetches user data from the API
 * @param {number} userId - The user ID
 * @returns {Promise<Object>} User data
 */
async function fetchUser(userId) {
    try {
        const response = await api.get(`/users/${userId}`);
        return response.user;
    } catch (error) {
        console.error('Failed to fetch user:', error);
        throw error;
    }
}
```

### Python (Workers)

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for functions
- Handle **exceptions** properly
- Keep functions **small and focused**

Example:
```python
async def handle_user_login(request):
    """
    Handle user login request.
    
    Args:
        request: The incoming request object
        
    Returns:
        Response with token and user data
    """
    try:
        body = await request.json()
        # Process login
        return create_response(data, status=200)
    except Exception as e:
        return create_response({'error': str(e)}, status=400)
```

## Testing

### Manual Testing

Before submitting a PR, test:

1. **All pages load** correctly
2. **Forms submit** properly
3. **Links navigate** correctly
4. **Responsive design** works on mobile
5. **Accessibility** with screen reader
6. **Cross-browser** compatibility

### Browser Testing

Test in:
- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Accessibility Testing

Use these tools:
- **axe DevTools** browser extension
- **WAVE** browser extension
- **Lighthouse** in Chrome DevTools
- Manual keyboard navigation

## Commit Messages

Write clear, descriptive commit messages:

**Good:**
```
Add user profile page

- Create profile.html with user info display
- Add profile styles to main.css
- Implement API endpoint for user data
```

**Bad:**
```
Update files
Fixed stuff
WIP
```

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

## Pull Request Process

1. **Update documentation** if needed
2. **Test thoroughly** on multiple browsers
3. **Ensure no console errors**
4. **Check accessibility**
5. **Write clear PR description**:
   - What changes were made
   - Why they were made
   - How to test them

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tested in Chrome
- [ ] Tested in Firefox
- [ ] Tested in Safari
- [ ] Mobile responsive
- [ ] Accessibility checked

## Screenshots
(if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console errors
```

## Areas to Contribute

### 🎨 Frontend Development

- **New pages** (user profiles, bug details, etc.)
- **UI components** (modals, dropdowns, etc.)
- **Responsive design** improvements
- **Accessibility** enhancements
- **Performance** optimizations

### ⚙️ Backend Development

- **API endpoints** for new features
- **Database schema** design
- **Authentication** improvements
- **Rate limiting** logic
- **Caching** strategies

### 📝 Documentation

- **User guides** and tutorials
- **API documentation** improvements
- **Architecture** documentation
- **Code comments** and examples
- **Translation** to other languages

### 🐛 Bug Fixes

Check the [Issues](https://github.com/OWASP-BLT/BLT-Next/issues) page for:
- Bugs labeled `good first issue`
- Bugs labeled `help wanted`

### 🚀 New Features

Propose and implement:
- **Gamification** features (badges, achievements)
- **Social features** (comments, likes)
- **Search** functionality
- **Filtering** and sorting
- **Notifications** system

## Project Structure

```
BLT-Next/
├── index.html              # Landing page
├── src/
│   ├── assets/
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript modules
│   │   └── images/        # Images and icons
│   ├── pages/             # Additional pages
│   └── workers/           # Cloudflare Workers
├── docs/                  # Documentation
├── .github/
│   └── workflows/         # CI/CD workflows
└── README.md
```

## Resources

- [OWASP BLT Documentation](https://owasp-blt.github.io/documentation/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [HTMX Documentation](https://htmx.org/docs/)
- [MDN Web Docs](https://developer.mozilla.org/)

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **OWASP Slack**: Join the #blt channel

## Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes
- Given contributor badge on profile

## License

By contributing, you agree that your contributions will be licensed under the GNU Affero General Public License v3.0.

---

Thank you for contributing to BLT-Next! Your efforts help make the internet more secure. 🚀

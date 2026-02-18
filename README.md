# BLT-Next: Modern Static Frontend Architecture

> **A fresh, modern design by removing non-core components to create a clear, enjoyable user experience focused on core value**

## 🚀 Overview

BLT-Next is the next-generation architecture for OWASP BLT (Bug Logging Tool), migrating from a Django monolith to a lightweight, performant static frontend with dynamic features powered by Cloudflare Python Workers.

## ✨ Key Features

- **⚡ Sub-200ms Global Response Times**: Optimized static assets served via GitHub Pages CDN
- **🎯 Progressive Enhancement**: Core functionality works without JavaScript, enhanced with HTMX
- **📦 Modular Architecture**: Clean separation of concerns with reusable components
- **🔒 Secure by Default**: Cloudflare Workers handle authentication and sensitive operations
- **🌍 Global CDN**: GitHub Pages provides worldwide distribution
- **💪 Maintainable**: Vanilla JS, modern CSS, and clear structure for easy contributions

## 🏗️ Architecture

### Frontend (GitHub Pages)
- **Static Assets**: HTML, CSS, JavaScript served via GitHub Pages
- **Framework**: Vanilla JS + HTMX for dynamic interactions
- **Styling**: Custom CSS framework (no dependencies)
- **Build**: Zero build step - works out of the box

### Backend (Cloudflare Python Workers)
- **API Endpoints**: Python workers handle dynamic features
- **Authentication**: Secure token-based auth
- **Database**: Integration with Cloudflare D1 or external DB
- **Performance**: Edge computing for sub-200ms responses

## 📁 Project Structure

```
BLT-Next/
├── index.html                  # Main landing page
├── src/
│   ├── assets/
│   │   ├── css/
│   │   │   └── main.css       # Custom CSS framework
│   │   ├── js/
│   │   │   └── main.js        # Main application logic
│   │   └── images/
│   ├── components/            # Reusable HTML components
│   ├── pages/                 # Static pages
│   │   ├── report-bug.html
│   │   ├── leaderboard.html
│   │   ├── projects.html
│   │   └── about.html
│   └── workers/               # Cloudflare Workers
│       └── main.py            # Main API worker
├── docs/                      # Documentation
├── _config.yml               # GitHub Pages config
└── .github/
    └── workflows/
        └── pages.yml         # GitHub Pages deployment
```

## 🚦 Getting Started

### Prerequisites

- Git
- Modern web browser
- (Optional) Python 3.11+ for local worker development
- (Optional) Node.js for running a local server

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/OWASP-BLT/BLT-Next.git
   cd BLT-Next
   ```

2. **Serve locally**
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Or using Node.js
   npx http-server -p 8000
   ```

3. **Open in browser**
   ```
   http://localhost:8000
   ```

### Cloudflare Workers Setup

1. **Install Wrangler CLI**
   ```bash
   npm install -g wrangler
   ```

2. **Configure Worker**
   ```bash
   cd src/workers
   wrangler init
   ```

3. **Deploy Worker**
   ```bash
   wrangler deploy
   ```

4. **Update API endpoint** in `src/assets/js/main.js`:
   ```javascript
   const CONFIG = {
       API_BASE_URL: 'https://your-worker.workers.dev',
   };
   ```

## 🎨 Features Implementation

### Core Features

- ✅ **Bug Reporting**: Intuitive form with HTMX for seamless submission
- ✅ **Leaderboard**: Dynamic ranking system loaded via API
- ✅ **Authentication**: Secure login/signup with JWT tokens
- ✅ **User Profiles**: User dashboard and activity tracking
- ✅ **Projects**: Company/project management
- ✅ **Rewards**: Gamification with points and badges

### Progressive Enhancement

1. **Base Layer**: Core HTML works without JavaScript
2. **Enhanced Layer**: HTMX adds dynamic interactions
3. **Rich Layer**: Vanilla JS provides advanced features

## 🔧 Configuration

### GitHub Pages

Enable GitHub Pages in repository settings:
1. Go to Settings > Pages
2. Source: Deploy from a branch
3. Branch: main / (root)
4. Save

### Environment Variables (Cloudflare)

Set these in Cloudflare Workers dashboard:
```bash
DATABASE_URL=your_database_url
JWT_SECRET=your_jwt_secret
ALLOWED_ORIGINS=https://owasp-blt.github.io
```

## 📊 Performance

- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Total Bundle Size**: < 100KB (uncompressed)
- **API Response Time**: < 200ms (global average)

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- **HTML**: Semantic, accessible markup
- **CSS**: BEM methodology, CSS variables
- **JavaScript**: ES6+, modular, documented
- **Python**: PEP 8 compliant

## 📝 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guide](docs/contributing.md)

## 🔒 Security

- All dynamic features handled by secure Cloudflare Workers
- CORS properly configured
- Input validation on both client and server
- JWT-based authentication
- No sensitive data in frontend code

## 📜 License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OWASP Community
- All contributors to the original BLT project
- GitHub for Pages hosting
- Cloudflare for Workers platform

## 📧 Contact

- **Project**: [OWASP BLT](https://owasp.org/www-project-bug-logging-tool/)
- **GitHub**: [OWASP-BLT](https://github.com/OWASP-BLT)
- **Issues**: [GitHub Issues](https://github.com/OWASP-BLT/BLT-Next/issues)

---

Made with ❤️ by the OWASP BLT community

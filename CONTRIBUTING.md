# Contributing to OWASP BLT-Next

Thank you for your interest in contributing to OWASP BLT! We welcome contributions from everyone.

## Getting Started

### 1. Fork the Repository
Fork the [BLT-Next](https://github.com/OWASP-BLT/BLT-Next) repository and clone it to your local machine.

### 2. Local Setup

You can choose between a direct local setup or using Docker.

#### Option A: Direct Local Setup (Recommended)
1.  **Install Node.js** (v18 or later)
2.  **Install Python** (for the Cloudflare Worker)
3.  **Install Dependencies**:
    ```bash
    npm install
    ```
4.  **Start Development Server**:
    ```bash
    npm run dev
    ```
    This will start a unified server at `http://localhost:8787` serving both the frontend and the backend API.

## Project Structure

- `src/index.html`: Main entry point
- `src/assets/`: CSS and JavaScript assets
- `src/pages/`: Static HTML pages for different features
- `workers/`: Cloudflare Worker (Python) backend logic

## Development Workflow

1.  Create a new branch for your feature or bugfix: `git checkout -b feature/my-new-feature`
2.  Make your changes.
3.  Test your changes locally.
4.  Commit your changes: `git commit -m "Add some feature"`
5.  Push to your fork: `git push origin feature/my-new-feature`
6.  Open a Pull Request.

## Coding Standards

- Use semantic HTML5 elements.
- Follow the existing CSS naming conventions.
- Ensure your JavaScript is well-commented.
- For backend changes, follow Python PEP 8 guidelines where possible.

## Need Help?

If you have any questions, feel free to open an issue or join our community discussions.

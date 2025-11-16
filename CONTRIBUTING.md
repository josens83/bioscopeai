# Contributing to BioscopeAI

Thank you for your interest in contributing to BioscopeAI! We welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please:
- Check existing issues to avoid duplicates
- Clearly describe the feature and its benefits
- Provide use cases and examples

### Code Contributions

#### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/josens83/bioscopeai.git
   cd bioscopeai
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install

   # Mobile
   cd ../mobile
   npm install
   ```

4. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed

5. **Run tests**
   ```bash
   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   npm test
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add awesome feature"
   ```

7. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Build process or auxiliary tool changes

Examples:
```
feat: add paper comparison feature
fix: resolve authentication token expiry issue
docs: update API documentation
test: add tests for RAG pipeline
```

#### Code Style

**Python (Backend)**
- Follow PEP 8
- Use Black for formatting
- Use type hints
- Write docstrings for functions and classes

**TypeScript/JavaScript (Frontend/Mobile)**
- Use ESLint configuration
- Use Prettier for formatting
- Use TypeScript types
- Write clear component documentation

#### Pull Request Process

1. **Update documentation** if you changed APIs or added features
2. **Add tests** for new functionality
3. **Ensure all tests pass** locally before submitting
4. **Update CHANGELOG.md** with your changes
5. **Reference related issues** in your PR description
6. **Request review** from maintainers

Your PR will be reviewed by maintainers. Be patient and responsive to feedback.

## 📋 Development Guidelines

### Backend Development

- Use async/await for database operations
- Follow FastAPI best practices
- Handle errors appropriately with proper HTTP status codes
- Log important operations using the logging system
- Write unit tests for business logic

### Frontend Development

- Use React hooks and functional components
- Implement proper loading and error states
- Use React Query for data fetching
- Keep components small and focused
- Write accessible UI (ARIA labels, keyboard navigation)

### Mobile Development

- Follow React Native best practices
- Test on both iOS and Android
- Handle different screen sizes
- Implement proper error handling
- Use secure storage for sensitive data

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
docker-compose up -d
# Run integration tests
docker-compose down
```

## 📚 Documentation

- Update README.md for major features
- Update API documentation in `docs/API.md`
- Add JSDoc/docstring comments to new code
- Update OpenAPI schema if you modify API endpoints

## 🔒 Security

If you discover a security vulnerability:
1. **DO NOT** create a public issue
2. Email security concerns to: security@bioscopeai.com
3. Include detailed description and steps to reproduce
4. Allow time for us to address the issue before public disclosure

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

- Create an issue for general questions
- Join our discussions on GitHub
- Email: support@bioscopeai.com

## 🎉 Recognition

Contributors will be recognized in our README and release notes!

Thank you for helping make BioscopeAI better! 🙏

## 🔐 Security Setup

### Environment Variables

This project uses environment variables for sensitive configuration. **Never commit the `.env` file to version control.**

#### Setup Steps:

1. Copy the example environment file:
```bash
   cp .env.example .env
```

2. Generate a secure JWT secret:
```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. Update `.env` with your generated secrets and strong passwords

4. Verify `.env` is in `.gitignore` (it should be by default)

### Production Deployment

For production environments:

- **Use a secrets manager**: AWS Secrets Manager, Railway Environment Variables, or similar
- **Rotate secrets regularly**: Implement key rotation policies
- **Use strong passwords**: Minimum 20 characters with mixed case, numbers, and symbols
- **Enable SSL/TLS**: For all database connections
- **Restrict network access**: Use VPCs and security groups
- **Enable audit logging**: Track all access to sensitive data

### Checking for Exposed Secrets

Before committing:
```bash
# Check if .env is tracked
git status

# If .env appears, immediately:
git reset .env
echo ".env" >> .gitignore
```
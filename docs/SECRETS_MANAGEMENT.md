# Secrets Management Guide

This document outlines how to manage sensitive configuration and credentials for the DaVinci Resolve MCP server.

## Overview

The DaVinci Resolve MCP server may need to handle sensitive information such as:
- API keys for external services
- Database credentials
- Authentication tokens
- Custom configuration paths

This guide covers secure handling of these secrets.

## Environment Variables

### Recommended Approach: Environment Variables

Store sensitive configuration in environment variables rather than code or configuration files.

```bash
# Linux/macOS
export API_KEY="your-secret-api-key"
export DATABASE_URL="postgresql://user:password@localhost/db"

# Windows PowerShell
$env:API_KEY="your-secret-api-key"
$env:DATABASE_URL="postgresql://user:password@localhost/db"

# Windows Command Prompt
set API_KEY=your-secret-api-key
set DATABASE_URL=postgresql://user:password@localhost/db
```

### Claude Desktop Configuration

When configuring the MCP server in Claude Desktop, use environment variables:

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "davinci-resolve-mcp",
      "args": ["mcp"],
      "env": {
        "API_KEY": "your-secret-api-key",
        "CUSTOM_CONFIG_PATH": "/secure/path/to/config"
      }
    }
  }
}
```

## Secure Storage Options

### 1. System Keyring/Keychain

For persistent secure storage:

**Windows:**
```powershell
# Use Windows Credential Manager
cmdkey /generic:"DaVinciResolveMCP_API_KEY" /user:"API_KEY" /pass:"your-secret-key"
```

**macOS:**
```bash
# Use Keychain
security add-generic-password -s "DaVinci Resolve MCP" -a "api_key" -w "your-secret-key"
```

**Linux:**
```bash
# Use Secret Service (GNOME) or KWallet (KDE)
# Implementation depends on desktop environment
```

### 2. External Secret Managers

For enterprise environments:

**AWS Secrets Manager:**
```python
import boto3

def get_secret():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='davinci-resolve-mcp/config')
    return response['SecretString']
```

**Azure Key Vault:**
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret():
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
    return client.get_secret("api-key").value
```

**HashiCorp Vault:**
```python
import hvac

def get_secret():
    client = hvac.Client(url='https://vault.example.com:8200')
    response = client.secrets.kv.v2.read_secret_version(path='davinci-resolve-mcp/config')
    return response['data']['data']
```

## Configuration File Security

### Encrypted Configuration Files

If you must use configuration files, encrypt sensitive data:

```python
from cryptography.fernet import Fernet
import json

def encrypt_config(data: dict, key: str) -> bytes:
    """Encrypt configuration data."""
    f = Fernet(key.encode())
    json_data = json.dumps(data).encode()
    return f.encrypt(json_data)

def decrypt_config(encrypted_data: bytes, key: str) -> dict:
    """Decrypt configuration data."""
    f = Fernet(key.encode())
    json_data = f.decrypt(encrypted_data).decode()
    return json.loads(json_data)
```

### Secure File Permissions

Set appropriate file permissions for configuration files:

**Linux/macOS:**
```bash
# Set restrictive permissions
chmod 600 config.json
# Owner read/write only

# Or use ACLs
setfacl -m u:username:r config.json
```

**Windows:**
```powershell
# Set restrictive permissions
icacls config.json /inheritance:r /grant:r "$env:USERNAME:(R,W)"
```

## Best Practices

### 1. Never Commit Secrets

- Use `.gitignore` to exclude configuration files with secrets
- Use pre-commit hooks to check for secrets
- Rotate secrets regularly

### 2. Principle of Least Privilege

- Grant only necessary permissions
- Use read-only credentials where possible
- Limit secret scope and lifetime

### 3. Secret Rotation

Implement automatic secret rotation:

```python
import time
from datetime import datetime, timedelta

class SecretRotator:
    def __init__(self, rotation_interval_days: int = 30):
        self.rotation_interval = timedelta(days=rotation_interval_days)
        self.last_rotation = datetime.now()

    def should_rotate(self) -> bool:
        return datetime.now() - self.last_rotation > self.rotation_interval

    def rotate_secret(self, old_secret: str) -> str:
        # Implement rotation logic (e.g., call API to generate new secret)
        new_secret = generate_new_secret()
        self.last_rotation = datetime.now()
        return new_secret
```

### 4. Audit Logging

Log secret access for security monitoring:

```python
import logging
from datetime import datetime

class AuditedSecretStore:
    def __init__(self):
        self.logger = logging.getLogger('secret_audit')

    def get_secret(self, key: str, user: str) -> str:
        secret = self._retrieve_secret(key)
        self.logger.info(f"Secret '{key}' accessed by user '{user}' at {datetime.now()}")
        return secret

    def _retrieve_secret(self, key: str) -> str:
        # Actual secret retrieval logic
        pass
```

## Development vs Production

### Development Environment

For development, use local configuration with dummy values:

```bash
# .env file (add to .gitignore)
API_KEY=dev-dummy-key
DATABASE_URL=sqlite:///dev.db
DEBUG=true
```

### Production Environment

For production, use secure secret management:

```bash
# Environment-specific secrets
export API_KEY="$(aws secretsmanager get-secret-value --secret-id prod/api-key --query SecretString --output text)"
export DATABASE_URL="$(vault kv get -field=url database/prod)"
```

## Security Checklist

- [ ] Secrets are not committed to version control
- [ ] Environment variables are used for configuration
- [ ] Configuration files have restrictive permissions
- [ ] Secrets are rotated regularly
- [ ] Access to secrets is logged and monitored
- [ ] Different secrets are used for different environments
- [ ] Secrets are encrypted at rest and in transit
- [ ] Backup procedures include secure secret handling

## Troubleshooting

### Common Issues

**"Permission denied" errors:**
- Check file permissions on configuration files
- Ensure the application has access to secret storage

**"Secret not found" errors:**
- Verify environment variable names
- Check secret store connectivity
- Confirm secret keys/names are correct

**"Invalid secret format" errors:**
- Validate secret encoding (base64, JSON, etc.)
- Check for special characters in secrets
- Verify secret expiration dates

## Support

For security-related issues or questions about secret management, please refer to:
- [SECURITY.md](SECURITY.md) - Security policy and vulnerability reporting
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- GitHub Issues - For bug reports and feature requests

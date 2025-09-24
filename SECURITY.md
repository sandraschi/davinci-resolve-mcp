# Security Policy

## Supported Versions

DaVinci Resolve MCP follows semantic versioning and provides security support for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in DaVinci Resolve MCP, please report it responsibly.

### Contact Information

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
- **Email**: sandra@sandraschi.dev
- **Subject**: [SECURITY] DaVinci Resolve MCP Vulnerability Report

### What to Include

When reporting a security vulnerability, please include:

1. **Description**: A clear description of the vulnerability
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Impact**: Description of the potential impact
4. **Affected Versions**: Which versions are affected
5. **Environment**: Your system configuration (OS, Python version, DaVinci Resolve version)
6. **Proof of Concept**: If available, a proof of concept demonstrating the vulnerability

### Response Timeline

- **Initial Response**: Within 24 hours of receiving the report
- **Vulnerability Assessment**: Within 3 business days
- **Fix Development**: Within 7-14 days for critical vulnerabilities
- **Public Disclosure**: After fix is deployed and tested

## Security Considerations

### Data Handling
- DaVinci Resolve MCP does not store or transmit user data to external servers
- All operations are performed locally on the user's system
- Project files and media remain under user control

### Network Communications
- MCP server runs locally on `127.0.0.1` by default
- No external network connections are made without explicit user configuration
- Claude Desktop communication uses stdio protocol (local process communication)

### Dependencies
- All dependencies are reviewed for security vulnerabilities
- Regular dependency updates are performed
- Security patches are applied promptly

### Authentication & Authorization
- No authentication is required to run the MCP server
- Access is controlled by the user's Claude Desktop configuration
- DaVinci Resolve operations respect the application's permission model

## Security Best Practices

### For Users
1. **Keep Software Updated**
   - Regularly update DaVinci Resolve MCP
   - Keep DaVinci Resolve updated to the latest version
   - Update Python and system dependencies

2. **Secure Configuration**
   - Only configure trusted MCP servers in Claude Desktop
   - Use strong passwords for DaVinci Resolve projects if applicable
   - Store configuration files securely

3. **Network Security**
   - Run the MCP server on localhost only
   - Do not expose the MCP server to external networks
   - Use firewalls to restrict access

### For Developers
1. **Code Review**
   - All code changes undergo security review
   - Dependencies are scanned for vulnerabilities
   - Input validation is implemented throughout

2. **Testing**
   - Security testing is performed on all releases
   - Fuzz testing for input validation
   - Integration testing with security scenarios

3. **Dependency Management**
   - Dependencies are pinned to specific versions
   - Regular dependency updates and security audits
   - Use of trusted package sources only

## Known Security Considerations

### DaVinci Resolve Integration
- Security depends on DaVinci Resolve's security model
- Project files may contain sensitive information
- Media files are handled according to DaVinci Resolve's permissions

### Python Environment
- Virtual environment usage is recommended
- Avoid running with elevated privileges
- Keep Python and pip updated

### File System Access
- MCP server requires access to DaVinci Resolve installation
- Project and media directories are accessed locally
- File operations respect system permissions

## Security Updates

Security updates will be:
- Released as patch versions (e.g., 0.1.1, 0.1.2)
- Documented in the CHANGELOG.md
- Announced through GitHub releases
- Backported to supported versions when applicable

## Disclaimer

This security policy applies to DaVinci Resolve MCP only. Security of DaVinci Resolve itself is the responsibility of Blackmagic Design. Security of Claude Desktop is the responsibility of Anthropic.

## Contact

For security-related questions or concerns:
- **Email**: sandra@sandraschi.dev
- **GitHub Issues**: For non-sensitive security questions (label as "security")

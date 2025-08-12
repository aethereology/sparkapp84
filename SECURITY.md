# Security Implementation Guide

## 🔒 Authentication System

### JWT-Based Authentication
- **Access Tokens**: 30-minute expiration
- **Refresh Tokens**: 7-day expiration  
- **Algorithm**: HS256 with configurable secret key
- **Default Users**: `admin/admin123`, `reviewer/reviewer123` (⚠️ Change in production!)

### API Endpoints
- `POST /auth/login` - Authenticate and get tokens
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout (client-side token disposal)
- `GET /auth/status` - Public auth system status

### Role-Based Access Control
- **admin**: Full system access
- **reviewer**: Data room and document access
- **user**: Basic API access

## 🛡️ Security Features Implemented

### 1. Square Webhook Security
✅ **HMAC-SHA256 Signature Verification**
```python
# Webhook signature validation
if not verify_square_webhook(raw, x_square_hmacsha256_signature):
    raise HTTPException(status_code=400, detail="Invalid signature")
```

✅ **Timestamp Validation**
- 5-minute tolerance window
- Prevents replay attacks

✅ **Rate Limiting**
- 100 requests/minute per IP
- Redis-based tracking with automatic expiration

✅ **Idempotency Protection**
- Duplicate event detection
- 24-hour cache for processed events
- Processing locks to prevent race conditions

### 2. API Security
✅ **Authentication Required**
- All sensitive endpoints require valid JWT token
- Role-based access control implemented

✅ **CORS Configuration**
- Configurable allowed origins
- Credential support enabled
- Exposed headers controlled

✅ **Input Validation**
- FastAPI Pydantic models for request validation
- Automatic error handling for malformed requests

✅ **Error Handling**
- Structured error responses
- Sensitive information filtering
- Comprehensive logging

### 3. Production Security
✅ **Environment-Based Configuration**
- Production mode disables API docs
- TrustedHost middleware for production
- Secure headers implementation

✅ **Logging & Monitoring**
- Structured logging with timestamps
- Request/response tracking
- Security event logging
- Error tracking with context

## 🚨 Security Checklist for Production

### CRITICAL - Must Complete Before Deployment

#### Authentication Security
- [ ] **Change default passwords** - Update `admin123` and `reviewer123` passwords
- [ ] **Generate strong JWT secret** - Replace `JWT_SECRET_KEY` with cryptographically secure key
- [ ] **Enable password complexity** - Implement strong password requirements
- [ ] **Add password hashing rounds** - Increase bcrypt rounds for better security

#### Environment Configuration  
- [ ] **Set production environment variables**:
  ```bash
  ENV=production
  JWT_SECRET_KEY=<strong-random-key-256-bits>
  CORS_ORIGINS=https://yourdomain.com
  ALLOWED_HOSTS=api.yourdomain.com,yourdomain.com
  ```
- [ ] **Configure secrets management** - Use Google Secret Manager or similar
- [ ] **Enable HTTPS only** - Configure SSL/TLS certificates
- [ ] **Set secure cookie flags** - httpOnly, secure, sameSite

#### Database Security
- [ ] **Replace fake user database** - Implement proper user storage
- [ ] **Add user registration flow** - Secure user onboarding
- [ ] **Implement user management** - Admin interface for user control
- [ ] **Add session management** - Token revocation and session control

#### Infrastructure Security
- [ ] **Configure firewall rules** - Restrict network access
- [ ] **Enable audit logging** - Comprehensive activity tracking
- [ ] **Set up monitoring alerts** - Security incident detection
- [ ] **Regular security scans** - Vulnerability assessments

### MEDIUM Priority

#### API Security Enhancements
- [ ] **Implement API rate limiting** - Global rate limits
- [ ] **Add request size limits** - Prevent DOS attacks
- [ ] **Enable security headers** - HSTS, CSP, X-Frame-Options
- [ ] **Add IP allowlisting** - Restrict admin access by IP

#### Webhook Security
- [ ] **Add webhook authentication logs** - Track all webhook attempts
- [ ] **Implement webhook retry logic** - Handle failed webhook processing
- [ ] **Add webhook rate limiting per source** - Prevent webhook flooding
- [ ] **Monitor webhook processing times** - Performance tracking

## 🔐 Environment Variables Reference

### Authentication
```bash
JWT_SECRET_KEY=<256-bit-hex-key>           # CRITICAL: Change in production
ACCESS_TOKEN_EXPIRE_MINUTES=30             # Token lifetime
REFRESH_TOKEN_EXPIRE_DAYS=7                # Refresh token lifetime
```

### CORS & Security
```bash
CORS_ORIGINS=https://app.yourdomain.com    # Allowed origins
ALLOWED_HOSTS=api.yourdomain.com           # Trusted hosts
ENV=production                             # Environment mode
```

### Webhook Security
```bash
SQUARE_WEBHOOK_SIGNATURE_KEY=<square-key>  # Square webhook key
WEBHOOK_RATE_LIMIT_PER_MINUTE=100         # Rate limit
WEBHOOK_TIMESTAMP_TOLERANCE=300           # 5 minutes
IDEMPOTENCY_KEY_TTL=86400                 # 24 hours
```

## 🚨 Incident Response

### Authentication Failures
1. **Invalid login attempts**: Monitor and alert on multiple failed attempts
2. **Token validation errors**: Check for malformed or expired tokens
3. **Unauthorized access**: Log and investigate access attempts to protected resources

### Webhook Security Issues
1. **Invalid signatures**: Alert on repeated signature failures from same IP
2. **Replay attacks**: Monitor for duplicate event IDs within time window
3. **Rate limit violations**: Track and potentially block suspicious IPs

### System Security Events
1. **Privilege escalation**: Monitor role changes and admin actions
2. **Data access patterns**: Track unusual data access or download patterns
3. **System configuration changes**: Alert on security setting modifications

## 📋 Security Audit Recommendations

### Regular Tasks (Monthly)
- Review user access and roles
- Audit authentication logs
- Check webhook processing logs
- Review rate limiting effectiveness

### Security Updates (Quarterly)
- Update dependencies to latest secure versions
- Review and rotate JWT secrets
- Security penetration testing
- Update security documentation

### Annual Security Review
- Complete security architecture review
- Third-party security audit
- Disaster recovery testing
- Security training updates

## 🆘 Emergency Contacts

### Security Incident Response
- **Technical Lead**: [Contact Info]
- **System Administrator**: [Contact Info]
- **Security Team**: [Contact Info]

### External Services
- **Square Support**: For webhook security issues
- **Cloud Provider**: For infrastructure security
- **Security Vendor**: For incident response support
# OAuth Setup Guide for HireFlow AI

## Overview
This document provides the OAuth redirect URLs needed for Google Cloud Console and Microsoft Azure Portal configuration.

## Google OAuth Setup

### Redirect URLs to Add in Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Select your OAuth 2.0 Client ID** (ID: 387382505084-m1tg4q71lulso2m33mr9a7ni8p6qddlt.apps.googleusercontent.com)
4. **Add these Authorized Redirect URIs**:

```
Production:
https://hireflow-app-1.preview.emergentagent.com/auth/google/callback

Development:
http://localhost:3000/auth/google/callback
```

### Scopes Requested by HireFlow AI:
- `openid` - User authentication
- `https://www.googleapis.com/auth/userinfo.email` - User email address
- `https://www.googleapis.com/auth/userinfo.profile` - User profile information
- `https://www.googleapis.com/auth/gmail.send` - Send emails on behalf of user
- `https://www.googleapis.com/auth/calendar` - Manage calendar events

### Testing Google OAuth:
1. GET `/api/oauth/google/url` - Get authorization URL
2. User authorizes in browser
3. POST `/api/oauth/google/callback?code={code}` - Exchange code for tokens

---

## Microsoft OAuth Setup

### Redirect URLs to Add in Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com/
2. **Navigate to**: Azure Active Directory → App Registrations
3. **Select your app** or create a new one
4. **Go to Authentication** → Add a platform → Web
5. **Add these Redirect URIs**:

```
Production:
https://hireflow-app-1.preview.emergentagent.com/auth/microsoft/callback

Development:
http://localhost:3000/auth/microsoft/callback
```

### Required API Permissions:
- `User.Read` - Read user profile
- `Mail.Send` - Send mail as user
- `Calendars.ReadWrite` - Read and write calendar events
- `offline_access` - Maintain access to data

### Environment Variables Needed:
```env
MICROSOFT_CLIENT_ID=<your_client_id>
MICROSOFT_CLIENT_SECRET=<your_client_secret>
MICROSOFT_TENANT_ID=common  # or your specific tenant ID
```

### Testing Microsoft OAuth:
1. GET `/api/oauth/microsoft/url` - Get authorization URL
2. User authorizes in browser
3. POST `/api/oauth/microsoft/callback?code={code}` - Exchange code for tokens

---

## Email Configuration Flow

### For Hiring Managers:

1. **Sign in/Register** with email/password OR use Google/Microsoft OAuth
2. **Connect OAuth Provider** (if not already connected):
   - Go to Settings → Integrations
   - Click "Connect Google" or "Connect Microsoft"
   - Authorize permissions for Email + Calendar
3. **Configure Email Settings**:
   - Go to Settings → Email Configuration
   - Select provider: Gmail, Outlook, or Custom SMTP
   - For Gmail/Outlook: Use connected OAuth account
   - For SMTP: Enter server details
   - Add email signature
   - Test configuration
4. **Start Hiring!** - Emails will be sent automatically:
   - Application confirmation
   - Shortlisted notification
   - Rejection (after configurable delay)
   - Interview invitation
   - Offer letters

---

## API Endpoints Reference

### OAuth Endpoints

#### Get Google OAuth URL
```http
GET /api/oauth/google/url
Authorization: Bearer {token}  # Optional - if provided, connects to existing account

Response:
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "redirect_uri": "https://hireflow-app-1.preview.emergentagent.com/auth/google/callback",
  "info": "Add this redirect URI to your Google Cloud Console"
}
```

#### Google OAuth Callback
```http
POST /api/oauth/google/callback
Content-Type: application/json

{
  "code": "authorization_code_from_google",
  "state": "user_id_or_new_user",
  "redirect_uri": "https://hireflow-app-1.preview.emergentagent.com/auth/google/callback"
}

Response:
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

#### Get Microsoft OAuth URL
```http
GET /api/oauth/microsoft/url
Authorization: Bearer {token}  # Optional

Response:
{
  "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?...",
  "redirect_uri": "https://hireflow-app-1.preview.emergentagent.com/auth/microsoft/callback",
  "info": "Add this redirect URI to your Azure App Registration"
}
```

#### Microsoft OAuth Callback
```http
POST /api/oauth/microsoft/callback
Content-Type: application/json

{
  "code": "authorization_code_from_microsoft",
  "state": "user_id_or_new_user",
  "redirect_uri": "https://hireflow-app-1.preview.emergentagent.com/auth/microsoft/callback"
}
```

#### Disconnect OAuth Provider
```http
POST /api/oauth/disconnect/{provider}
Authorization: Bearer {token}

# provider: "google" or "microsoft"

Response:
{
  "message": "Google disconnected successfully"
}
```

### Email Configuration Endpoints

#### Create/Update Email Config
```http
POST /api/email-config
Authorization: Bearer {token}
Content-Type: application/json

{
  "provider": "gmail",  # gmail, outlook, or smtp
  "from_email": "hr@company.com",
  "from_name": "Company HR Team",
  "signature": "<p>Best regards,<br>HR Team</p>",
  "smtp_config": {  # Only for SMTP provider
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "user@example.com",
    "password": "app_password",
    "use_tls": true
  }
}
```

#### Test Email Configuration
```http
POST /api/email-config/test
Authorization: Bearer {token}

Response:
{
  "success": true,
  "message": "Test email sent successfully to user@example.com",
  "provider": "gmail"
}
```

---

## Architecture Notes

### Background Job Processing
- **RQ (Redis Queue)** processes all email and calendar operations asynchronously
- **Multiple Queues**: email, resume, calendar, report, default
- **Worker Process**: `/app/backend/worker.py` processes jobs

### Email Workflow
1. Application submitted → Application processor runs
2. Resume parsed and evaluated by AI
3. Email job queued based on evaluation:
   - Strong match → Immediate confirmation + shortlisted email
   - Good fit → Confirmation email only
   - Not a fit → Confirmation email + scheduled rejection (48h delay)

### Calendar Integration
- Automatically creates calendar events for scheduled interviews
- Syncs with hiring manager's Google Calendar or Outlook Calendar
- Sends meeting invites to candidates
- Handles conflict detection and rescheduling

---

## Security Best Practices

1. **OAuth Tokens**: Stored encrypted in database (implement encryption in production)
2. **SMTP Passwords**: Should be app-specific passwords, not account passwords
3. **Rate Limiting**: Implemented on all API endpoints (max 100 requests/minute)
4. **CORS**: Configured to allow only authorized origins
5. **Token Expiry**: Access tokens expire in 30 minutes, refresh tokens in 7 days

---

## Troubleshooting

### "OAuth not configured" Error
- Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in backend `.env`
- For Microsoft, also set `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`, `MICROSOFT_TENANT_ID`

### "Redirect URI mismatch" Error
- Ensure the redirect URI in the OAuth provider console EXACTLY matches the one used in the request
- Check for trailing slashes, http vs https

### Emails Not Sending
1. Check email configuration: `GET /api/email-config`
2. Test configuration: `POST /api/email-config/test`
3. Check Redis is running: `redis-cli ping`
4. Check RQ worker is running: `ps aux | grep worker.py`
5. Check worker logs: `tail -f /var/log/supervisor/rq-worker.log`

### Calendar Events Not Creating
1. Verify user has connected Google or Microsoft OAuth
2. Check calendar permissions were granted during OAuth flow
3. Ensure OAuth tokens are not expired (refresh if needed)

---

## Production Deployment Checklist

- [ ] Set strong `SECRET_KEY` in environment variables
- [ ] Configure proper `CORS_ORIGINS` (not `*`)
- [ ] Set up HTTPS for all OAuth redirect URIs
- [ ] Enable Redis persistence for job queue reliability
- [ ] Set up monitoring for RQ workers
- [ ] Implement OAuth token encryption in database
- [ ] Set up email sending rate limits with provider
- [ ] Configure backup SMTP for failover
- [ ] Set up logging and alerting for failed jobs
- [ ] Test OAuth flows with real Google/Microsoft accounts
- [ ] Load test email sending with 1000+ concurrent jobs

---

## Support

For issues or questions, check:
- Backend logs: `/var/log/supervisor/backend.err.log`
- Worker logs: `/var/log/supervisor/rq-worker.log`
- Redis logs: `/var/log/redis/redis-server.log`

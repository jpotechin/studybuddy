# Vercel Environment Variables Setup

## Environment Variables in Vercel Dashboard

Go to your Vercel project → Settings → Environment Variables and add:

### Backend Variables (Python/FastAPI)

```
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-super-secret-key-change-this-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password
```

### Frontend Variables (React/Vite)

```
VITE_API_BASE_URL=https://your-app-name.vercel.app
```

## Important Notes

1. **VITE\_ prefix is required** for frontend variables
2. **Backend variables** don't need prefixes
3. **Set for all environments**: Production, Preview, and Development
4. **No quotes needed** in Vercel dashboard
5. **Case sensitive** - use exact variable names

## Local Development

Keep your separate `.env` files for local development:

- `backend/.env` - for backend variables
- `frontend/.env` - for frontend variables

## Deployment Process

1. Set environment variables in Vercel dashboard
2. Push to your main branch
3. Vercel automatically deploys
4. Check function logs if there are issues

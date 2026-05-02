# SkillBarter Deployment

## Architecture

- Frontend: Vercel
- Backend: Render
- Database: Supabase Postgres
- Auth: JWT via `SECRET_KEY`
- Realtime: FastAPI WebSockets on the Render backend

## 1. Frontend on Vercel

### Build settings

- Framework preset: `Vite`
- Build command: `npm run build`
- Output directory: `dist`

### Environment variable

- `VITE_API_URL=https://your-backend.onrender.com`

### Routing

- SPA routing is handled by [vercel.json](./vercel.json), which rewrites app routes to `index.html`.

## 2. Backend on Render

### Start command

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Render blueprint

- Use [render.yaml](./render.yaml)
- Health check path: `/health`

### Environment variables

- `APP_ENV=production`
- `DATABASE_URL=<supabase-postgres-connection-string>`
- `SECRET_KEY=<long-random-secret>`
- `JWT_ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=30`
- `FRONTEND_ORIGIN=https://your-frontend.vercel.app`
- `CORS_ORIGINS=https://your-frontend.vercel.app,https://www.your-frontend.vercel.app`
- `AUTO_CREATE_TABLES=false`

## 3. Database on Supabase

Use the Supabase Postgres connection string as `DATABASE_URL`.

Recommended pooled format:

```env
DATABASE_URL=postgresql+psycopg://postgres.<supabase-project-ref>:<db-password>@aws-0-<region>.pooler.supabase.com:6543/postgres
```

## 4. Migrations

Run Alembic before or immediately after first deploy:

```bash
python -m alembic upgrade head
```

If you use the Render shell, run that command there against the production environment variables.

## 5. Security Checklist

- Never commit `.env`
- Set a strong `SECRET_KEY` in Render only
- Keep `ACCESS_TOKEN_EXPIRE_MINUTES` short in production
- Use `https://` frontend/backend URLs only
- Keep `AUTO_CREATE_TABLES=false` in production and rely on Alembic

## 6. WebSockets

- The frontend derives `wss://` automatically from `VITE_API_URL`
- Render web services support WebSockets on the same backend host
- No separate socket server is required

## 7. Recommended Deployment Order

1. Provision Supabase Postgres and copy the pooled `DATABASE_URL`
2. Create the Render backend service and set backend environment variables
3. Run `python -m alembic upgrade head` against production
4. Deploy the Vercel frontend with `VITE_API_URL` pointing to Render
5. Set `FRONTEND_ORIGIN` and `CORS_ORIGINS` on Render to the final Vercel domain
6. Verify:
   - `GET /health`
   - register/login
   - `/matchmaking`
   - social requests
   - chat over WebSockets

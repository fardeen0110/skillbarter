# TODO - CORS fix + DB schema migration for messages

- [x] Locate FastAPI CORSMiddleware configuration.
- [x] Locate allowed origins config in backend/config.py.
- [x] Improve origin parsing/normalization to match browser Origin.
- [x] Update Render env var values for Vercel origin.

- [x] Inspect SQLAlchemy Message model (done: backend/models.py shows message_type + attachment_* + delivered_at/read_at).

- [x] Inspect current `messages` table schema in DB (migration history shows messages columns were partially applied; runtime error indicates missing columns).

- [x] Generate Alembic migration to add missing columns to `messages` table.

- [ ] If migrations can’t be generated, produce raw SQL ALTER TABLE statements.
- [ ] Patch repo with new Alembic migration.
- [ ] Explain why dashboard_summary crashes.
- [ ] Explain why browser shows CORS error even though backend crash is the underlying issue (CORS middleware vs network error masking).
- [ ] Generate final git patch.


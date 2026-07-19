# YeS-TR Copilot Development Instructions

## Architecture
- frontend: Next.js + TypeScript
- backend: FastAPI + Python
- database/auth/storage: Supabase
- vector search: pgvector

## Security
- Never expose the Supabase service role key to frontend code.
- Every backend project endpoint must validate user access.
- Searches must always be filtered by project_id.
- Do not log access tokens, API keys, or uploaded document contents.

## Coding standards
- Use explicit TypeScript types.
- Use Pydantic models for API input and output.
- Add meaningful error handling.
- Keep functions small and testable.
- Do not silently catch exceptions.
- Avoid rewriting working modules without a clear reason.

## Validation
After changes, run:
- frontend lint
- frontend type-check
- backend tests
- relevant API smoke tests

## Product constraints
- The system provides preliminary decision support, not official certification.
- LLM output must be grounded in retrieved sources.
- The LLM must not calculate official YeS-TR scores.
- Low-quality OCR content must not be searchable.
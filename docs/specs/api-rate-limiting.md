# API Rate Limiting Specification

> **Nota de migración (2026-04-15):** El backend fue migrado de Redis (SSPL) a **Valkey 9.x** (BSD-3-Clause, Linux Foundation). Los requerimientos y escenarios documentados aquí siguen vigentes. Las referencias a "Redis" en los escenarios aplican a Valkey.

## Purpose

This specification defines the rate limiting behavior for the OpenRAG public API. The system MUST protect against abuse and enable cost control through configurable request limits per API key.

## Requirements

### Requirement: Rate Limit Enforcement

The system SHALL enforce rate limits on all API v1 endpoints based on the API key tier.

A request to any `/api/v1/*` endpoint MUST be evaluated against the key's tier limit before execution.

#### Scenario: Request Within Limit

- GIVEN an API key with "free" tier (100 requests/minute)
- WHEN the client makes a request
- THEN the request proceeds normally
- AND the response includes `X-RateLimit-Limit: 100`
- AND the response includes `X-RateLimit-Remaining: 99`
- AND the response includes `X-RateLimit-Reset: {timestamp}`

#### Scenario: Request Exceeds Limit

- GIVEN an API key with "free" tier that has made 100 requests in the current window
- WHEN the client makes another request
- THEN the response is HTTP 429 Too Many Requests
- AND the response includes `Retry-After: {seconds}`
- AND the response includes `X-RateLimit-Limit: 100`
- AND the response includes `X-RateLimit-Remaining: 0`

#### Scenario: Enterprise Key Unlimited

- GIVEN an API key with "enterprise" tier (unlimited)
- WHEN the client makes any number of requests
- THEN all requests proceed normally
- AND response headers include `X-RateLimit-Limit: unlimited`

### Requirement: Tier Configuration

The system MUST support configurable rate limit tiers stored with each API key.

The API key document in OpenSearch MUST include a `tier` field with values: `free`, `pro`, or `enterprise`.

#### Scenario: Default Tier Assignment

- GIVEN a newly created API key without explicit tier
- WHEN the key is stored
- THEN the tier is set to `free` by default

#### Scenario: Pro Tier

- GIVEN an API key with "pro" tier
- WHEN the client makes requests
- THEN the limit is 1000 requests/minute

### Requirement: Redis Backend

The system SHOULD use Redis as the primary storage for rate limit counters, with fallback to in-memory for development.

When Redis is unavailable, the system MUST fall back to an in-memory counter.

#### Scenario: Redis Available

- GIVEN Redis is available at the configured endpoint
- WHEN a request is made
- THEN the counter is incremented in Redis
- AND the counter uses the API key hash as the key

#### Scenario: Redis Unavailable

- GIVEN Redis is unavailable
- WHEN a client makes a request
- THEN the request proceeds with in-memory counter
- AND a warning is logged about fallback mode

### Requirement: Rate Limit Headers

The system MUST include standard rate limit headers in all API responses.

#### Scenario: Headers Present

- GIVEN a valid API request
- WHEN the response is generated
- THEN these headers are present:
  - `X-RateLimit-Limit` (number or "unlimited")
  - `X-RateLimit-Remaining` (number)
  - `X-RateLimit-Reset` (Unix timestamp)

#### Scenario: No Headers on Error

- GIVEN a request that fails before rate limiting check (e.g., invalid API key)
- WHEN the error response is generated
- THEN rate limit headers are NOT included
- AND the error response is 401/403 as appropriate

## Acceptance Criteria

- [ ] Free tier: 100 requests/minute enforced
- [ ] Pro tier: 1000 requests/minute enforced
- [ ] Enterprise tier: unlimited requests
- [ ] HTTP 429 returned when limit exceeded
- [ ] Headers X-RateLimit-* present in all v1 responses
- [ ] Redis fallback to in-memory works
- [ ] Default tier is "free" for new keys

## Notes

- Tier limits stored in API key document in OpenSearch
- Middleware applies to all `/api/v1/*` endpoints
- Redis is optional (fallback to in-memory)

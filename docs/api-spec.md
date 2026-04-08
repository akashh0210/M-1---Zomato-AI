# API Contract - Phase 2

## Endpoints

`GET /locations`
Fetches a list of all available localities.

`POST /recommendations`

## Request Body

```json
{
  "location": "bangalore",
  "budget": 1500.0,
  "cuisine": ["north indian", "chinese"],
  "min_rating": 3.8,
  "additional_preferences": ["family-friendly", "quick service"]
}
```

## Request Field Rules

- `location`: required string, normalized to lowercase
- `budget`: required positive max budget limit (float)
- `cuisine`: required string or string list, empty values rejected
- `min_rating`: required float in range `0.0-5.0`
- `additional_preferences`: optional string or string list



## Success Response

```json
{
  "query": {
    "location": "bangalore",
    "budget": 1500.0,
    "cuisine": ["north indian", "chinese"],
    "min_rating": 3.8,
    "additional_preferences": ["family-friendly", "quick service"]
  },
  "suggestions": [],
  "recommendations": [
    {
      "rank": 1,
      "restaurant_name": "Example Restaurant",
      "location_city": "bangalore",
      "cuisines": ["north indian", "chinese"],
      "rating": 4.3,
      "estimated_cost_for_two": 1500.0,
      "explanation": "Matches your location, budget, and preferred cuisine with strong rating.",
      "confidence": 0.86
    }
  ],
  "message": null
}
```

## Fallback Behavior

- If no exact matches found, API returns:
  - empty `recommendations`
  - cuisine `suggestions` where possible
  - a user-friendly `message`

## Phase 3 Deterministic Retrieval

Hard filters are applied in this order:
- location exact match
- budget band cost filter
- minimum rating threshold
- at least one cuisine match

Candidates are then scored with weighted soft ranking:
- `rating_score` (45%)
- `cuisine_similarity` (25%)
- `cost_fit_score` (20%)
- `preference_match_score` (10%)

## Phase 4 LLM Reranking (Groq)

- The API passes the Phase 3 shortlist to Groq LLM for final reranking and richer explanation text.
- Expected LLM JSON fields: `rank`, `restaurant_name`, `rationale`, `tradeoffs`, `confidence`.
- Guardrails:
  - reject restaurants not present in shortlist
  - enforce explanation and tradeoff length limits
  - fallback to deterministic ranking on parse/API failure
- Configure in `.env`:
  - `GROQ_API_KEY=<your_key>`
  - optional: `GROQ_MODEL=<model_name>`

## Error Responses

- `422`: Validation error for invalid payload
- `503`: Processed data file unavailable (run Phase 1 pipeline first)


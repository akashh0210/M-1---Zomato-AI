Replace free-text location with a dropdown of available localities (fetch from processed data).
Fix location extraction: filter/store locality correctly (locality vs restaurant names currently appearing).
Replace budget categories (low/med/high) with numeric budget input (min/max or single value) and update LLM prompt/logic to match numeric budget.
Remove the “shortlist size” input (use a fixed cutoff, e.g., first 50 filtered items sent to LLM).
Reduce duplicate restaurant results: detect and dedupe duplicates (handle multiple outlets vs same restaurant) — provide examples to reproduce and ask model to find pattern.
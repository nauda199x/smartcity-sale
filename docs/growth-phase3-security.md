# Saved-search privacy model

- `saved_searches` is not readable by `anon`.
- Every CRUD policy checks `user_id = (select auth.uid())`.
- The public marketplace keeps anonymous browsing available; authentication is required only when the user chooses to save a search.
- If the visitor is not signed in, only the filter criteria are temporarily stored in localStorage so the intent can be restored after login. No listing-account privileges are granted by this flow.
- New-match counts query only already-approved public listings and compare `approved_at` with the user's private `last_seen_at` marker.

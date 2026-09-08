# Marketplace parity with Lumi Hanoi — 8 September 2026

Compared Smart City `22c070c2` with Lumi `4a778024`. This change applies to
`nauda199x/smartcity-sale` and `timmuasmartcity.com`.

| Capability | Smart City before | Result |
|---|---|---|
| Public inventory | At most 120 records, local filtering/sorting | Server filtering and sorting, 10 records per page, exact totals, shareable filters, back/forward navigation |
| Price and room filters | Min/max could overwrite each other; historical plus-room labels varied | Combined price/area predicates; 1PN+/1PN+1 and 2PN+ variants remain searchable |
| Admin inventory | At most 300 records | 20/50/100 per page; whole-inventory keyword, phone, phase, tower, unit, status and date sorting |
| Admin overview | Local counters | Full counts for all, pending, active, expiring and reported listings |
| Moderation | Mostly individual actions | Select multiple listings, approve/renew, hide, mark sold/rented, preserve partial-failure details |
| Editing | No concurrent edit guard | Existing updated_at checked before saving or acting, typed content retained on failure |
| Reports | Reports attached to listings | Unresolved-report queue, view report details, resolve only the reviewed reports |
| Posting | Mobile wizard, saved draft, title helper, image compression, preview/removal already present | Preserved; added cover selection and permitted concise nonblank descriptions |
| Listing detail | Static and dynamic experiences differed | Shared template, thumbnail gallery, swipe/zoom, share, device-local saved state, collapsed long description, sticky contact actions |
| Related information | Basic facts | Links to 49 existing tower plans, same-tower and same-unit inventory, map, posting date |
| Listing state | Static content until rebuild | Live status check disables contact/report actions for unavailable listings |
| Views | Absent | Deduplicated view counter; excludes common bots; repeated views within one hour count once; does not change posting/update dates |
| Public-field privacy | Table-wide anonymous read grant | Only public listing columns readable; email, exact unit code and private notes excluded |
| SEO inventory | Detail URLs and ItemList existed, fetch capped at 500 | Crawlable inventory cards and numbered pages; complete fetching beyond 500; grouped phase/unit pages when inventory exists |
| Asking prices | Editorial/reference material | Additional table grouped by transaction, phase and room type from actual active public listings |
| Refresh | Daily scheduled fallback plus admin dispatch | Five-minute scheduled fallback; unchanged snapshots skip publication; data fetch failure blocks an empty replacement deployment |
| Discovery and trust | Project and transaction navigation, policies existed | Stronger posting CTA, About/Contact routes, native footer links to existing privacy/terms pages |
| Performance | Some image lazy loading | Lightweight paged requests, skeletons, stale-request cancellation, bounded intent-based navigation prefetch |

Both projects currently use anonymous posting with an administrator account. Public
poster accounts, payments and paid VIP subscriptions are not live Lumi features and
are not represented as completed in this parity update. The content, photographs,
floor plans and property taxonomy remain specific to Smart City. Existing Plus-room
types and the exclusion of Duplex from the posting choices are preserved.

## Validation

- 23 JavaScript regression checks cover 625-record admin pagination, authorization,
  concurrent refresh, request races, optimistic locking and partial bulk failures.
- Seven Python checks cover HTML/JSON-LD injection, shared detail controls, dates,
  23-record static pagination, category metadata, exact tower links, and source
  fetching past 500 records or failing safely.
- Live public API verified 3 sale listings and 1 rental listing, combined filters,
  and detail lookup at the time of testing.
- Database counter assertions ran in a transaction and were rolled back: one
  increment for repeated views, unchanged updated_at, hidden visitor data and no
  authenticated access to the anonymous counter endpoint.
- Public privileges verified: phone remains readable; private email/exact unit
  code and visitor fingerprints do not.
- Existing portal, SEO, floor-plan and dossier validation gates are retained.
- Database advisors reported no new external table exposure. Existing Auth leaked
  password protection remains disabled; see the
  [Supabase password protection setting](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection).

Browser end-to-end and screenshot testing were not performed. GitHub scheduled jobs
may run later than the nominal five-minute interval. A static URL becomes crawlable
after its successful publication; inclusion does not guarantee Google indexing.

# Madvisor daily update (instructions for the cloud routine)

You keep `feed.json` up to date: a public list of real, currently open opportunities for UK creatives. The Madvisor app downloads this list, and each person's phone works out which ones fit them. **You never see or handle anyone's personal details, and the feed must never contain any.**

## Hard rules

- Never make up opportunities, links, fees, deadlines, chart positions or eligibility rules. Every fact comes from a page you opened with WebFetch during this run. If the page doesn't state something, leave the field empty (`null`, `""` or `[]`).
- Only add items with a working link and a deadline that hasn't passed (or a rolling/open call). Confirm the deadline on the organiser's own page; round-ups and newsletters are leads only. If sources disagree, use the organiser's date and say so in `notes`.
- No personal data in the feed: no names of private individuals, emails or phone numbers. Venue addresses and organisations are fine.

## Steps

1. Run `python3 tools/check_feed.py` first. It removes expired items.
2. Find new open opportunities across the UK, aiming for **15–30 new items per run** when they exist, spread across:
   - Disciplines: musicians of every kind (rappers/MCs, singers, DJs, producers, bands, songwriters, instrumentalists), plus visual artists, photographers, filmmakers, dancers, poets/spoken word and writers.
   - Regions: every English region, plus Scotland, Wales and Northern Ireland. Include local gigs, open mics, showcases and open calls, not just national funds.
   - Types: Gig, Grant / funding, Competition, Other (residencies, showcases, courses, commissions, open calls).
   Sources to check every run (open the page and add only rounds that are open now): Help Musicians (Fast Track, Fast Track Live, other funds), PRS Foundation deadlines page (prsfoundation.com/funding-support/deadlines/), PPL Momentum Music Fund, FAC Step Up Fund, Sound and Music opportunities, BBC Introducing (local shows' calls), Arts Council England, Creative Scotland, Arts Council of Wales, Arts Council of Northern Ireland, a-n.co.uk opportunities, Arts Jobs (artsjobs.org.uk), Opportunity Tuesday, Ditto Music funding round-up, British Council music funding list, plus local listings sites and promoters found by searching. Then run several varied searches of your own.
3. Skip anything whose `link` or `name` is already in `feed.json`.
4. Add each new item to `opportunities` with exactly these fields:
   - `id`: lowercase-hyphenated short slug, unique
   - `name`, `type` (one of `Gig`, `Grant / funding`, `Competition`, `Other`)
   - `disciplines`: from `Any creative`, `Any musician`, `Rapper / MC`, `Singer`, `DJ`, `Producer`, `Band`, `Songwriter`, `Instrumentalist`, `Visual artist`, `Photographer`, `Filmmaker`, `Dancer`, `Poet / spoken word`, `Writer`, `Other creative`. Use who the page says it's for.
   - `genres`: only if the page restricts or targets genres (lowercase), else `[]`
   - `deadline` (`YYYY-MM-DD` or `null`), `rolling` (true/false), `event_date` (`YYYY-MM-DD` or `null`)
   - `where`: short human description; `location`: where someone must physically be (venue address with postcode if given, or town), `null` for online/apply-from-anywhere; `lat`/`lon`: `null` (the check script fills them)
   - `area_restriction`: where applicants must live, only if stated (e.g. `["UK"]`, `["England"]`, `["Glasgow"]`), else `[]`
   - `min_age`, `max_age`: numbers or `null`
   - `career_stages`: only if restricted, from `just starting`, `emerging`, `developing`, `established`, else `[]`
   - `requirements`: short text of other conditions (e.g. "£500 music income in last 12 months"), else `""`
   - `fee`: amount/fee as stated, else `""`
   - `link`, `notes` (one line: what it is and the main catch), `verified` and `added`: today's date
5. Refresh `captions`: for `music` and `creative` (and any specific discipline key you think needs its own, e.g. `"DJ"`), write 3 short templates: `Instagram`, `TikTok`, `Booking bio`. Use ONLY these placeholders for personal details: `{name}`, `{discipline}`, `{genres}`, `{based_in}`, `{contact}`. State no other facts about the person (no achievements, gigs, releases, stats). No pronouns for the person: use `{name}` or first person. Vary them from the previous day's.
6. Run `python3 tools/check_feed.py` again. If it prints "NOT SAVED", fix the listed problems and run it again until it prints "ok".
7. Commit only `feed.json` with the message `Daily update YYYY-MM-DD: N new, M removed` and push to `main`.

# Madvisor

Open gigs, grants and competitions for UK creatives: musicians, DJs, visual artists, filmmakers, dancers, writers and more.

**Privacy:** Madvisor has no accounts, no database and no server. `feed.json` is a public list of opportunities, updated daily by a Claude routine following [ROUTINE.md](ROUTINE.md). Each person's profile, matching, statuses and captions live only in their own browser (`localStorage`). The only outside call the app makes is a postcodes.io lookup of the person's town for distances, made directly from their device.

- `index.html`: the app (add it to your phone's home screen)
- `feed.json`: the shared opportunities list
- `tools/check_feed.py`: validates the list, removes expired items, adds coordinates, and blocks personal data

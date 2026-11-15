# NutriLens Content Repo

This repository holds the **live content** for the NutriLens app. Anything you change here reaches every installed app **without a Play Store release** — the app checks this repo on every launch.

| File | What it controls | Version field |
|---|---|---|
| `topics.json` | The 6 learning topics and all their cards (English + Tamil + Hindi) | `"content_version": "YYYY-MM-DD"` (date string) |
| `foods.json` | The food database used by the Food tracker search | `"content_version": 2` (whole number) |

Served to the app through jsDelivr:

- `https://cdn.jsdelivr.net/gh/arulprakashp-cmd/nutrilens-content@main/topics.json`
- `https://cdn.jsdelivr.net/gh/arulprakashp-cmd/nutrilens-content@main/foods.json`

> ⚠️ This repo must stay **public**. jsDelivr cannot read private repos (the app silently keeps old content if it gets a 404).

---

## The 4-step update routine (both files)

1. **Edit** the JSON file (any editor; VS Code shows syntax errors as you type).
2. **Bump `content_version`** — the app only replaces its cached copy if the new version is *higher*.
   - `topics.json`: set it to today's date, e.g. `"2026-06-18"`.
   - `foods.json`: add 1, e.g. `2` → `3`.
3. **Validate**: `python3 validate.py` (catches broken JSON, duplicate IDs, missing translations).
4. **Commit & push** to `main`.

```bash
python3 validate.py && git add -A && git commit -m "Add ragi dosa, fix protein card 04 typo" && git push
```

### How fast do users see it?

| Step | Time |
|---|---|
| jsDelivr picks up the push | ~10 min (up to 12 h). Force it: open `https://purge.jsdelivr.net/gh/arulprakashp-cmd/nutrilens-content@main/foods.json` (or `topics.json`) in a browser |
| App downloads it | Next launch (checked at most every 5 min) — downloads in background |
| User sees it | The launch **after** that |

Forgot to bump `content_version`? Nothing happens — users keep the old content. Bump and push again.

---

## Updating `foods.json`

```jsonc
{
  "schema_version": 1,            // never change
  "content_version": 2,           // ← bump by 1 every edit
  "categories": {                 // key → label shown in the app (emoji optional)
    "grain": "🌾 Grains",
    "south": "🫓 South Indian"
  },
  "foods": [
    {
      "id": "f214",               // unique, NEVER reuse or rename an existing id
      "name": "Ragi Dosa",        // what users search for
      "category": "south",        // must be one of the keys in "categories"
      "serving": "1 pc (60g)",    // free text, shown under the name
      "cal": 110,                 // per serving
      "protein": 3.2,             // grams per serving
      "carbs": 21,
      "fat": 1.1
    }
  ]
}
```

**Add a food** — append an object with a new `id` (`f<next number>`), bump `content_version`.

**Fix a value** — edit `cal`/`protein`/etc. in place. Past meals users already logged keep the old numbers (they're stored on-device); new logs use the new values.

**Rename a food** — change `name` only. Keep the `id`.

**Remove a food** — delete the object. Users who pinned it as a favourite or logged it keep working (the data is on their phone); it just stops appearing in search.

**Add a category** — add a key to `categories` first, then reference it from foods.

Search matches on `name` (case-insensitive, partial). Add common spellings into the name if needed, e.g. `"Chapati / Roti / Phulka"`.

---

## Updating `topics.json`

Structure (simplified):

```jsonc
{
  "schema_version": 1,
  "content_version": "2026-06-18",      // ← today's date on every edit
  "topics": [
    {
      "topic_id": "topic_protein",
      "key": "protein",                  // route key — don't change
      "title": "The Protein Story",
      "subtitle": "Why it matters · every body · every age",
      "emoji": "💪",
      "icon_name": "fitness",            // Ionicons name
      "description": "10 cards · Cell repair, amino acids …",   // keep the card count accurate
      "card_count": 10,                  // must equal cards.length
      "order": 1,
      "translations": { "ta": { "title": "…", "subtitle": "…", "description": "…" }, "hi": { … } },
      "cards": [
        {
          "card_id": "protein_01",       // unique
          "number": "01",
          "label": "Reality Check",      // small overline on the card
          "icon": "⚠️",
          "title": "India Has a Hidden Protein Gap",
          "order": 1,
          "content": { "type": "stats", "body": "…", "stats": [ { "value": "73%", "label": "…" } ] },
          "translations": {
            "ta": { "title": "…", "body": "…", "stats": [ { "label": "…" } ] },
            "hi": { "title": "…", "body": "…", "stats": [ { "label": "…" } ] }
          }
        }
      ]
    }
  ]
}
```

### Fix a typo / reword a card
Edit `title` or `content.body` (English) and the same field inside `translations.ta` / `translations.hi`. Bump the version. Done.

### Add a card
1. Copy an existing card **of the same `content.type`** inside the topic and paste it where you want it.
2. Give it a new `card_id` (e.g. `protein_11`) and set `number`/`order` for every card after it.
3. Update `card_count` and the number in `description` (e.g. `"11 cards · …"`).
4. Fill `translations.ta` and `translations.hi` — untranslated cards fall back to English, which looks odd when the user has picked Tamil.

### Reorder cards
Change `order` (and `number` so the on-card label matches). The app sorts by `order`.

### Remove a card
Delete the object, renumber the rest, fix `card_count` and `description`.

### Card content types you can use
Each `content.type` is drawn by a dedicated layout in the app. Copy an existing card of that type to get the exact field names.

| `type` | Best for |
|---|---|
| `stats` | 2–4 big numbers with a one-line label |
| `benefits` | Icon + title + description list |
| `comparison` | Macro kcal/g bars |
| `split_comparison` | Two-column good vs bad lists |
| `process` | Numbered steps |
| `checklist` | Tick-box action items |
| `summary` | Key takeaways + daily targets + checklist (closing card) |
| `targets` | "Who → how much" table |
| `timeline` | Year/era milestones |
| `myths` | Myth vs fact pairs |
| `swaps` | "Instead of X → eat Y" with impact |
| `meal_plan` | Breakfast/lunch/snack/dinner with grams |
| `protein_plan`, `protein_bars`, `fat_bars`, `amino_acids` | Protein/fat specific visuals |
| `gi_scale`, `gi_chart`, `sugar_comparison` | Carb/GI visuals |
| `fat_roles`, `fat_types`, `saturation_chart`, `omega_balance`, `cholesterol`, `cooking_oils`, `fat_targets` | Fat-topic visuals |

**Adding a brand-new type requires an app update** — the JSON alone can't invent layouts.

### Add a new topic
Possible, but needs one app update first (home-screen colour + Ionicons mapping for the new `key`). Prepare the JSON here, then ask for the app change.

---

## Keeping the app repo in sync

Fresh installs ship with whatever is bundled in the app at build time (`frontend/assets/data/topics.json` and `foods.json`). Before each Play Store build, copy the latest files from this repo into the app so new users don't start on stale content:

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/arulprakashp-cmd/nutrilens-content@main/topics.json > frontend/assets/data/topics.json
curl -fsSL https://cdn.jsdelivr.net/gh/arulprakashp-cmd/nutrilens-content@main/foods.json  > frontend/assets/data/foods.json
```

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Pushed, waited, nothing changed | `content_version` not bumped, or not higher than before. Bump and push. |
| Still nothing | jsDelivr cache — open the purge URL above, relaunch the app twice. |
| `validate.py` fails | Read the message: it names the file, the id and the problem. Usually a trailing comma, a duplicate `id`, or `card_count` ≠ number of cards. |
| Tamil/Hindi shows English text | That card has no `translations.ta` / `.hi` entry (or the key is misspelled). |
| Food not found in search | Check spelling of `name`; search is partial but must match characters in order. |

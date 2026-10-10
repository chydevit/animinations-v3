# Archive: authentic images

Put the image files in `img/`, and give each one an entry in `manifest.json`. Only use free licences
(public domain, CC0, CC BY, CC BY-SA), checked on the source page. The credits are built from the
`attribution_line` field.

```json
{
  "file": "img/spk_prasat_yeai_poeun.jpg",
  "title": "original file title",
  "object_name": "English label shown on screen",
  "object_name_km": "Khmer label",
  "object_date": "7th century CE (photo 2015)",
  "holding_institution": "in situ / National Museum of Cambodia …",
  "find_place": "Sambor Prei Kuk, Kampong Thom",
  "author": "photographer",
  "source_page_url": "https://commons.wikimedia.org/wiki/File:…",
  "licence": "CC BY-SA 4.0",
  "attribution_line": "Author / CC BY-SA 4.0 / via Wikimedia Commons",
  "authenticity_note": "what this image really shows, and what it does not",
  "suggested_chapter": 1
}
```

Use them in `script_src.py` with `PH("spk_prasat_yeai_poeun.jpg", ["a3"])` for a photo, or `MC(...)` for a museum card.

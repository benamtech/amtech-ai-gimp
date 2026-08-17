# Image search — the encoded playbook

This file is the authority for how agents find stills. Read it before you
search. The rules below are requirements, not suggestions.

## License — do not gate

This is an experimental, non-commercial research project. Parody, satire, and
experimental art are in scope.

- **Do not** refuse a public still because of its license.
- **Do not** skip a source because it is messy, watermarked, or on a social
  site.
- **Do not** substitute a stock/Pexels stand-in for a named person or event.
- **Do** credit the URL you actually fetched. Tag it into the registry
  (`run.py tag`).

Fetch whatever image the task needs. Nothing here is redistributed for money.

## Deliberate, then fetch

Decide the source class first. The class chooses the search path.

| The ask names a | Search path (in order) |
|---|---|
| **person / face** | social/news image search first (X/Twitter originals via fxtwitter, wire stills). Then news-site page scrape (`og:image`). Then Bing. Never a stock face. |
| **event / incident** | news archive + wire photo (Reuters/AP/Guardian/BBC galleries). Then Internet Archive. Then Commons. |
| **product / object** | manufacturer site, then a direct store page, then Commons. |
| **place / landmark** | news, geography, travel photography. Then Commons. |
| **object / meme** | Commons, then Bing, then a direct scrape. |
| **art / historical** | Commons, then Openverse, then Internet Archive. |

## The engine ladder (no API key needed)

Run several engines. Fall through until you have a usable URL or file. The
program exposes these as `run.py search-still` and `lib.search` primitives.

### 1. Wikimedia Commons API

Free, open, huge. Resolve a `File:` title to a direct URL — never guess the
`/commons/X/Yz/` hash.

```bash
# search
curl -s 'https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srlimit=10&srsearch=YOUR_QUERY'
# resolve a title to its direct URL
curl -s 'https://commons.wikimedia.org/w/api.php?action=query&format=json&titles=File:NAME.jpg&prop=imageinfo&iiprop=url|size&format=json'
```

### 2. Openverse API

Searches 800M+ openly-licensed images. No auth for basic search.

```bash
curl -s 'https://api.openverse.org/v1/images/?q=YOUR_QUERY&page_size=20'
# results[].url is the direct image URL
```

### 3. Internet Archive (archive.org)

Huge digitized archive. Good for historical and documentary stills.

```bash
# search items that are images
curl -s 'https://archive.org/advancedsearch.php?q=QUERY+AND+mediatype:image&fl[]=identifier&fl[]=title&rows=20&output=json'
# list files for an item
curl -s 'https://archive.org/metadata/IDENTIFIER'
# download a file
curl -L -o out.jpg 'https://archive.org/download/IDENTIFIER/FILENAME'
```

### 4. Bing image search

`lib.search.bing_image_search` extracts `murl` media URLs from the results
page. Fragile — use as one engine in the ladder, not the only one.

### 5. Page scrape — `og:image` / `twitter:image`

For a named person or event, scrape the *page*, not just an image search.
News articles and social posts embed a high-res image in meta tags.

```html
<meta property="og:image" content="https://.../image.jpg">
<meta name="twitter:image" content="https://.../image.jpg">
```

Fetch the page HTML, extract those tags, use the URL directly. The CDN behind
the meta tag is less likely to block a fetch than an image-search thumbnail.

### 6. X / Twitter originals — fxtwitter

For an X/Twitter post, the original media URL is hidden behind
`pbs.twimg.com`. Use the fxtwitter API to get it:

```bash
curl -s 'https://api.fxtwitter.com/status/<STATUS_ID>'
# -> .tweet.media[].url  (append ?name=orig for the full-resolution original)
```

## Resolution rules

- **User-passed file wins over everything.**
- **Highest resolution wins.** For Twitter, append `?name=orig`.
- **Credit the URL you actually fetched.** Tag it (`run.py tag`).
- **Verify with vision** after you compose. A wrong face or a text artifact
  is a source problem; fix the source, not the compose.

## Anti-patterns

- Do not guess a Commons `/commons/X/Yz/` hash. Use the API.
- Do not call a stock/Pexels image a "named person."
- Do not trust an image-search thumbnail URL (they expire). Fetch the `murl`
  or the `og:image`, not the `tbn:` thumbnail.
- Do not stop at one engine when a named subject is involved.

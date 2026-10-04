# Search metadata

The web owns one public route list in [`shared/site.ts`](../web/shared/site.ts).
Each page supplies Spanish title and description copy from
[`messages.ts`](../web/app/messages.ts) to `useSiteSeo`. That composable emits
the page title, description, Open Graph and Twitter metadata, and a canonical
URL. The configured origin is in [`nuxt.config.ts`](../web/nuxt.config.ts).

Nuxt prerenders `/sitemap.xml` and `/robots.txt`. The sitemap uses the public
route list. `robots.txt` allows crawling and points to the configured sitemap.
The committed [`og-image.png`](../web/public/og-image.png) is the social image;
the SVG artwork remains available beside it.

Run the root-path check after generation:

```sh
cd web
bun run generate
bun run check:seo
```

GitHub Pages supplies `PAGES_BASE_URL` during deployment. Check the repository
subpath locally with the same generated-output gate:

```sh
PAGES_BASE_URL=/wawapacha/ bun run generate
PAGES_BASE_URL=/wawapacha/ bun run check:seo
```

The checker verifies every public route, `lang="es"`, page metadata, canonical
paths, the social image, sitemap entries and the robots sitemap path. It is
implemented in [`check-seo.ts`](../web/scripts/check-seo.ts).

# Search metadata

The public route list is `publicRoutes` in
[`shared/site.ts`](../web/shared/site.ts). Each page passes Spanish title and
description copy from [`messages.ts`](../web/app/messages.ts) to
[`useSiteSeo`](../web/app/composables/useSiteSeo.ts), which sets the page title,
description, Open Graph and Twitter metadata, and the canonical URL. The site
origin is `runtimeConfig.public.siteOrigin` in
[`nuxt.config.ts`](../web/nuxt.config.ts).

Nuxt prerenders `/sitemap.xml` and `/robots.txt`. The sitemap lists the public
routes. `robots.txt` allows crawling and points to the sitemap.

The social image is the committed [`og-image.png`](../web/public/og-image.png),
1200×630, because crawlers do not reliably render SVG. Its source artwork is
[`og-image.svg`](../web/public/og-image.svg).

## Check

After generation, check the root-path output:

```sh
cd web
bun run generate
bun run check:seo
```

GitHub Pages serves the site from a repository subpath, which the deploy
workflow passes as `PAGES_BASE_URL`. Check the subpath build locally the same
way:

```sh
PAGES_BASE_URL=/wawapacha/ bun run generate
PAGES_BASE_URL=/wawapacha/ bun run check:seo
```

[`check-seo.ts`](../web/scripts/check-seo.ts) verifies, for every public route,
`lang="es"`, the title, description, Open Graph and Twitter tags, the social
image path and the canonical path. It also verifies that the sitemap lists the
public routes and that `robots.txt` names the sitemap.

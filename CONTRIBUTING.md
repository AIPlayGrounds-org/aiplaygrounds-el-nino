# Contribuir

## Ramas y PR

- `main` es lo que se publica: cada push despliega la web.
- Trabaja en una rama con nombre `tipo/tema` (`docs/…`, `feature/…`) y abre un PR a `main`.
- Un PR hace una cosa. Si depende de otro PR abierto, parte de su rama y dilo en la descripción.
- El PR pasa las comprobaciones de [`ci.yml`](.github/workflows/ci.yml) antes de fusionarse.

## Antes de abrir el PR

```sh
cd pipeline && uv run pytest
bun run generate
```

## Decisiones

Una decisión nueva se propone como entrada en [`docs/decisiones.md`](docs/decisiones.md), en el mismo PR que la aplica.

## Una fuente nueva

1. Una ficha en [`docs/fuentes/`](docs/fuentes/README.md) a partir de [`_plantilla.md`](docs/fuentes/_plantilla.md), con veredicto ✅.
2. Un módulo en `pipeline/src/wawapacha_pipeline/sources/` que cumple [`docs/datos.md`](docs/datos.md), registrado en `cli.py`, con un test sobre una copia real del archivo original.
3. Un notebook en `notebooks/` que importa el módulo y muestra cada paso. Un test falla si define funciones.
4. El JSON publicado en `data/`, con `wawapacha-pipeline run <id>`.

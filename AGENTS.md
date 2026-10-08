# Agent instructions

- Touch only the files owned by the task; report a needed change outside that
  scope instead of making it.
- Do not infer permission to edit a file from convenience or proximity.
- Treat [`docs/architecture.md`](docs/architecture.md) as the map of existing
  code and [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md) as the workflow.
- Never hand-edit generated files. Regenerate `docs/sources.md` and
  `web/app/types/dataset.ts` with their documented commands.
- Write docs, registry fields and code in English. Keep product UI copy and
  domain names such as El Niño Costero, ENFEN and SENAMHI in Spanish.
- Run the checks in [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md#checks)
  and the checks named by the task before handing work off.
- Do not put history, decision notes, status reports, proposals or working notes
  in the repository. Use git history and the task report instead.
- Keep one source of truth per rule and link to it rather than copying it.

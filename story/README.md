# Story (parked)

Story work starts after the code split is done. The app already reads
`story/nodes/<node_id>.yaml` through `GET /api/story/{node_id}` and shows nothing if the file
is missing, so writers can add files later without touching code.

Rules:
- Story is fiction; numbers are not. Never put statistics, course names, or employers in story text.
- Personas are synthetic and must be labelled as such.
- Encouraging tone. The mentor suggests; the user decides.

Format: see `nodes/_template.yaml`.

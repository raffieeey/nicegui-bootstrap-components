# Visual matrix

The L4 visual and accessibility layer covers Mode × theme × breakpoint.

## Coverage

Mode and theme are separate routes. Combined with each breakpoint they form
the matrix (4 routes × 3 viewports).

**Mode**

- Mode A — `/mode-a`
- Mode B — `/mode-b`

**Theme**

- light — `/light`
- dark — `/dark`

**Breakpoint**

- sm — 576 × 800
- md — 768 × 900
- lg — 1280 × 900

Accessibility is checked on the application root. Impacts of `critical` or
`serious` fail the matrix.

## How to run

```
pytest --visual
```

Without `--visual`, matrix tests are deselected. An infrastructure check still
runs in the default suite so a missing harness fails clearly.

The app under test is taken from `NGBC_VISUAL_BASE_URL` (default
`http://127.0.0.1:8080`).

## Baselines

PNG baselines live in `tests/visual/baselines/`. A missing baseline is written
on first run and comparison is skipped with a message to re-run. Later runs
compare bytes and fail with both baseline and actual paths on mismatch.

## Release checklist

- visual matrix green

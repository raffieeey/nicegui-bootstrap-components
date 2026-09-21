# DBC 2.0.4 value semantics — verified from installed source (2026-09-20)

Evidence base: `dbc.Input.__doc__` (docstring prop specs) and the transpiled
component bundle `dash_bootstrap_components/_components/dash_bootstrap_components.min.js`
in the dbc-ref venv. Quotes are from the minified `Input` implementation.

## Input.debounce

Docstring: `debounce (boolean | number; default False)`. propTypes:
`oneOfType([bool, number])`.

Verified JS behavior (minified, deobfuscated names):

- `onChange`: `O ? (Number.isFinite(O) ? (clearTimeout(B.current), B.current = setTimeout(K, O)) : noop) : K()`
  - `debounce=false` → publish `setProps` on every change.
  - `debounce=true` → onChange does nothing; publishing happens only on Enter (`onKeyUp`) or blur (`onBlur`).
  - `debounce=N` (number) → publish N ms after typing stops (trailing timer).
- `onBlur` / `onKeyUp(Enter)`: increment `n_blur`/`n_submit` and, when
  `debounce === true`, also flush the pending value.

Conclusion for the library contract: the compatibility surface accepts
`bool | number` exactly as DBC 2.0.4 does (all three behaviors are oracle
behavior, not inventions). A trailing-debounce *int* beyond DBC's behavior
is not needed and must not be flagged as a compat contract; the manifest
`dbc_type` for debounce is `boolean|number`.

## Input.value publishing

- `value: string | number; optional`.
- DBC does NOT convert an empty text field to `None`; the published value is
  the DOM value (empty string on clear). Numeric `None`-publishing is a
  **native extension** of this library, not DBC semantics. The earlier
  simplification "DBC keeps boolean" is corrected here and in the manifest
  notes.

## Select value stringiness

- `Select` option dicts: `{"label": ..., "value": string|number, "disabled": bool, "title": string}`.
- The selected `value` prop is `string | number` (or list, for multiple).
- DOM select semantics stringify option values in the DOM; React preserves
  the prop types through the JSON round-trip. The library will preserve
  numbers through props and only stringifies inside the DOM control.

## Table.from_dataframe

- `index: bool = True` default (DBC `_table.py`); verified in the schema
  extraction (`default: true`).

These notes are embedded in `contracts/dbc-2.0.4.json`
(`value_semantics_notes` + per-component `notes` fields) and are the
authority for L1/L2 value tests in phases 8 and 9.
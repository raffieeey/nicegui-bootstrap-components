# Changelog

All notable changes to this project are documented in this file. The format is
based on Keep a Changelog and this project adheres to Semantic Versioning.

## [0.1.3] - 2026-11-05

### Fixed

- Propagate Python-side `.value` assignments to the native DOM-facing value
  properties for Input, Textarea and Select.
- Keep Select option selection flags synchronized with programmatic value changes.
- Add regression coverage for server-side value updates.

Thanks to @evnchn for [#2](https://github.com/raffieeey/nicegui-bootstrap-components/pull/2).

## [0.1.2] - 2026-11-05

### Security

- Preserve Button, NavLink and Breadcrumb attribute values as structured data
  instead of parsing interpolated property strings.
- Ignore server-side clicks on disabled ListGroupItem components.

### Fixed

- Remove remote font imports from bundled themes so they remain self-contained.
- Fully hide dismissed fade alerts and their interactive descendants; reopening
  remains supported. Dismissal now hides immediately rather than animating out.

### Changed

- Reject unsupported component persistence modes with a clear error rather than
  silently discarding state. The shared Tabs persistence map has been removed.
  Built-in browser storage is not implemented; use application-managed storage.

## [0.1.1] - 2026-10-09

### Added

- `wrap=True` on `Stack` / `stack()` adds Bootstrap's `flex-wrap`, so long
  horizontal rows flow onto the next line instead of overflowing narrow
  viewports.

### Fixed

- Container-style helpers (`card_header`, `card_body`, `button`, and other
  `BootstrapElement` subclasses) accept a positional text label and can also
  be used as context managers; the label renders first and block contents are
  appended. Passing element children together with a context manager still
  raises `ChildrenError`, now with a message that names the fix.
- Documented that `setup()` is safe before pages exist (it queues shared head
  HTML and registers static files without creating elements).

## [0.1.0] - 2026-09-26

### Added

- Complete Bootstrap 5 component surface with native (`bs`) and DBC-compat
  (`dbc`) APIs.
- Themes and icons.
- Style modes and color modes.
- Persistence and navigation adaptations.
- Examples, documentation site, and visual harness.

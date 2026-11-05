# Changelog

All notable changes to this project are documented in this file.

## [0.1.2] - 2026-11-05

### Security

- Preserve Button, NavLink and Breadcrumb attribute values as structured data instead of parsing interpolated property strings.
- Ignore server-side clicks on disabled ListGroupItem components.

### Fixed

- Remove remote font imports from bundled themes so they remain self-contained.
- Fully hide dismissed fade alerts and their interactive descendants; reopening remains supported. Dismissal now hides immediately rather than animating out.

### Changed

- Reject unsupported component persistence modes with a clear error rather than silently discarding state. The shared Tabs persistence map has been removed.
- Built-in browser storage is not implemented; use application-managed storage.

## [0.1.1] - 2026-10-09

### Fixed

- Allow text labels in Bootstrap context-manager composition without rejecting valid child elements.
- Add opt-in `Stack(wrap=True)` support for narrow responsive layouts.
- Add regression coverage and clarify composition/setup behavior in the documentation.

## [0.1.0] - 2026-09-26

### Added

- Complete Bootstrap 5.3 component surface (66 exports) on native and compat surfaces
- 25 Bootswatch themes
- Bootstrap Icons + Font Awesome assets
- Scoped and unscoped style modes
- Light/dark color modes
- Adapted persistence and navigation helpers
- Examples gallery and templates
- MkDocs documentation site
- Visual/a11y harness

### Notes

API modelled on dash-bootstrap-components 2.0.4 with adaptations documented in
the compatibility guide.

# Compatibility

The compat surface (`dbc`) targets dash-bootstrap-components 2.0.4. Names,
constructor props, and structural CSS classes follow that reference. Dash
runtime features that have no NiceGUI equivalent are adapted or excluded as
listed below.

| Category | DBC 2.0.4 | This library |
| --- | --- | --- |
| Callbacks | Dash callback graph | NiceGUI handlers (`on_click`, `on_change`, and related) |
| Persistence | Dash `persistence` / `persisted_props` | Persist analogue (`persist="local\|session"`, public `id` required) |
| Loading | Dash loading wrapper | Explicit `loading` |
| Pattern-matching IDs | Dash `MATCH` / `ALL` / `ALLSMALLER` | Excluded |
| `external_link` on Button | Anchor behaviour in Dash | Applied only when the Button is rendered as an anchor |

See the repository SUPPORT.md for the per-component matrix.

!!! warning

    Ports from Dash apps are not drop-in. There is no React or Dash runtime
    and no callback graph; event handling and state live in NiceGUI.

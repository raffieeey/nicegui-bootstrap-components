# nicegui-bootstrap-components — Technical Design Document

**Status:** Implementation-ready  
**Revision:** 1  
**Compatibility oracle:** dash-bootstrap-components 2.0.4 (tag / PyPI, 2025-08-20)  
**Host framework baseline:** NiceGUI 3.17.1 (2026-09-18)  
**CSS / behavior baseline:** Bootstrap 5.3 (DBC 2.0.4 theme URLs pin 5.3.6; current Bootstrap docs identify 5.3.8 — see Open question 1)  
**Assessment date of source research:** 2026-09-20  
**Distribution (proposed):** `nicegui-bootstrap-components`  
**Import package:** `nicegui_bootstrap_components`

This document is the single source of truth for implementation. Facts about DBC and NiceGUI are taken from the pinned research. Library contracts that are *new* are labelled as such. Anything not established by the research is an **Open question** with a proposed default (Section 12). Implementers must not “fill gaps” by copying React-Bootstrap’s extra component namespace, Dash callback semantics, or Quasar widget APIs.

---

## 1. Executive summary

**nicegui-bootstrap-components** is a NiceGUI-native Bootstrap 5 component library whose public catalogue, constructor vocabulary, composition model, and observable state match dash-bootstrap-components (DBC) 2.0.4 as closely as a different runtime allows.

DBC 2.0.4 exports **66 components** from 27 modules, plus theme and icon *stylesheet constants* and `Table.from_dataframe`. It is not a thin set of Bootstrap class helpers: it is generated Dash/React component classes, React-Bootstrap behavior, some native HTML, and *externally supplied* Bootstrap CSS. A NiceGUI equivalent must reproduce **public contracts and user-visible behavior**, not Dash’s serialization, `setProps`, callback graph, or React runtime.

NiceGUI 3.x already provides the extension mechanisms required: `ui.element` over native HTML or custom Vue components, slots, Python and JS event handlers, `run_method` / `run_javascript`, observable props/classes/styles, and third-party asset registration. The library will use those mechanisms. It will **not** restyle Quasar widgets to look like Bootstrap, will **not** inject HTML strings as the primary composition model, and will **not** claim that existing Dash applications run unchanged.

Three compatibility surfaces are in scope:

| Dimension | Commitment |
|---|---|
| Component coverage | All 66 DBC 2.0.4 exports, including small structural pieces (`ModalTitle`, `InputGroupText`, `PopoverBody`, …). Jumbotron is a **recipe**, not an export. Rejected historical names stay rejected. |
| Portable API and behavior | Names, documented props, aliases, defaults, enum semantics, child composition, grid math, and observable values (`value`, `is_open`, `active_tab`, `n_clicks`, …) as specified per component. |
| Framework-dependent behavior | Dash callbacks, Dash persistence, Dash loading-context selectors, Dash pattern-matching IDs, and DBC’s Dash-oriented `Link` internals are **not** reimplemented. NiceGUI handlers, bindings, an explicit optional persistence helper, and explicit loading/busy props replace them and are documented as adaptations. |

The product exposes **two Python APIs over a shared implementation**:

1. **Native API** (`nicegui_bootstrap_components.bs`): snake_case factories, context managers, NiceGUI `on_*` handlers, bindable values.
2. **DBC compatibility API** (`nicegui_bootstrap_components.dbc`): PascalCase constructors, DBC prop names (including documented camelCase leftovers such as `enforceFocus`), `children=`, `n_clicks` / `n_submit` counters, and the same markup/behavior.

The two surfaces are **not** the same class object. Each public name is a thin per-surface subclass (or factory that instantiates one) of a private shared implementation; the surface is recorded on the instance at construction so validation that diverges (native extensions vs DBC enums, warnings vs errors) is enforceable. See 3.4.1.

Architecture in one line: **typed component contracts → NiceGUI elements (structural Python / interactive Vue) → Bootstrap 5 markup + controlled browser behavior → versioned CSS coexistence and theme layer.**

The two gates that decide whether the library is shippable are (1) **CSS coexistence** with Quasar and Tailwind, and (2) **DOM ownership** for overlays and transitions. Both are prototyped before the inventory is implemented (Section 10, phases 0–3). CSS coexistence requires assigning library stylesheets to NiceGUI’s pre-declared `overrides` cascade layer — unlayered injection cannot beat Quasar `!important` (Section 3.8).

Documentation and examples mirror DBC’s information architecture: per-component family pages with live examples + generated prop tables, the same sidebar slug order, a hosted gallery (Iris, Graphs in Tabs, Simple sidebar) plus repository templates, and versioned docs. Documentation text is neutral technical writing. The published codebase contains no build-tool watermarks, no generation footers, and no chatty comments.

---

## 2. Goals and non-goals

### 2.1 Goals

1. **Catalogue parity.** Ship equivalents of all 66 DBC 2.0.4 component exports listed in Section 4. Exceptions require an explicit written justification in this TDD or a later approved amendment. No extra names inferred from React-Bootstrap (`Dropdown`, `PaginationItem`, `CarouselItem`, `CardTitle`, `CardText`, etc.).
2. **Contract parity for portable behavior.** Match DBC names, defaults, enum vocabularies, composition (e.g. `Tabs` consumes `Tab` children; `Carousel` consumes item dicts; `Pagination` generates its own items), grid semantics, and observable state shapes.
3. **NiceGUI-native usage.** Idiomatic context-manager composition, typed constructors, Python event handlers, value bindings, and stable element instances that survive unrelated UI updates.
4. **Bootstrap visual and DOM fidelity inside the supported styling mode.** Markup and class names are Bootstrap 5, not Quasar. Users can apply familiar Bootstrap utilities via `class_name` / `.classes()`.
5. **Docs parity.** Per-component (or family) pages with lead, narrative, live examples, source, and argument reference. Sidebar component order matches DBC’s 30 slugs, including Jumbotron as a composition recipe. Additional category navigation is allowed *in addition to* that alphabetical/DBC order, not instead of it.
6. **Gallery parity.** Runnable single-file examples per component, composite layout examples, three hosted applications with the same pedagogical purpose as DBC’s Iris / Graphs in Tabs / Simple sidebar, plus templates analogous to DBC’s multi-page sidebar/navbar set.
7. **Installable OSS package.** `pip install` of the wheel does not require Node, Sass, or a CDN. Assets are pinned and bundled. `py.typed` is shipped. Python ≥ 3.10. NiceGUI 3.x as specified in Section 9.
8. **Human-authored public surface.** No AI branding anywhere in code, comments, docs, metadata, or examples. Comments only where a conventional human author would leave them. Examples are idiomatic and copy-pasteable.
9. **Machine-readable compatibility manifest.** Every export has a versioned schema: props, aliases, defaults, events, slots, styling targets, support status (`supported` / `adapted` / `unsupported` / `extension`) **per surface** (`native` / `compat`). Docs tables and CI consistency checks are generated from it.
10. **Two documented styling modes:** Bootstrap-first pages and mixed-page scoped Bootstrap. Neither mode is “dump unscoped Bootstrap into a default NiceGUI app and hope.” Both modes inject library CSS into cascade `layer(overrides)`.

### 2.2 Non-goals

1. **Running Dash applications unchanged.** No callback graph, no `Input`/`Output`/`State`, no `dash.ctx`, no `window.dash_component_api`.
2. **Reimplementing Dash persistence, loading context, or pattern-matching IDs** as silent drop-in semantics. Optional *analogues* are allowed if labelled as such.
3. **Restyling Quasar / Tailwind widgets** to impersonate Bootstrap. `ui.button` is not `bs.button`.
4. **Shipping a second Vue or React runtime** inside the page.
5. **Pixel-identical React-Bootstrap DOM** (data attributes, React-internal wrappers). The contract is Bootstrap-compatible markup, classes, accessibility tree, and behavior — not React’s internal structure.
6. **A data-grid engine.** `Table` is a styled HTML table plus optional `from_dataframe`. No built-in sort/filter/virtualization.
7. **A searchable multi-select.** DBC `Select` is a native single `<select>`. Multi-select / typeahead are out of the 2.0.4 inventory; if added later they are separately named extensions.
8. **Nested Bootstrap modals.** Bootstrap documents one modal at a time. This library does not invent nested-modal support in v1.
9. **Interactive popover focus trapping** beyond what Bootstrap documents. Rich interactive popover content is Vue-owned children; keyboard policy is specified, not oversold.
10. **Automatically disabling the host app’s Tailwind** on import.
11. **Compatibility aliases for DBC-removed names** (`CardColumns`, `CardDeck`, `FormGroup`, `InputGroupAddon`, `Jumbotron`, `ListGroupItemHeading`, `ListGroupItemText`, `Carousel.ride`, `DropdownMenu.addon_type` / `.right`, `Navbar.light`, `NavbarSimple.light`, `Popover.innerClassName` / `inner_class_name`, `Table.dark`, all `_timestamp` props). Constructors and props that DBC 2.0.4 rejects stay rejected, with clear errors.
12. **A generic HTML attribute passthrough on every component.** DBC itself does not guarantee this (e.g. Spinner’s styling surface is specialized; Button `external_link` must not leak onto a non-link `<button>`).

### 2.3 Definition of “parity” (release gate)

The project may claim **“DBC 2.0.4 API parity on NiceGUI 3”** only when all of the following are true:

- All 66 exports exist under both API surfaces.
- The compatibility manifest has a disposition for every DBC 2.0.4 constructor argument and documented observable (mandatory / adapted / deprecated-accepted / excluded), **per surface**, and CI fails on drift.
- Portable behaviors in Section 4 have automated tests (Python + real browser where JS is involved).
- Dash-specific items in Section 4.0.8 are documented as excluded or adapted, never silently ignored when a caller would reasonably expect an effect.
- Visual tests cover Bootstrap-first and mixed mode for the prototype slice and for overlays.
- Docs pages exist for the 30 DBC component slugs (Jumbotron = recipe) plus themes, icons, FAQ/quickstart analogues.
- The three gallery apps run from the published wheel.

Parity is **not** claimed for incomplete subsets, and is **not** claimed against DBC 2.0.5rc4 or `main`.

### 2.4 Audiences

| Audience | What they get |
|---|---|
| NiceGUI application authors | `bs.*` components that look and behave like Bootstrap 5. |
| Authors porting DBC layouts | `dbc.*` constructors and props that translate mechanically for portable UI. |
| Implementers | This TDD, the manifest schema, and the phase list. |
| Downstream tools | Shipped JSON schema in the wheel (addresses the class of problem reported as DBC issue #1163: missing machine-readable metadata). |

Revision note (R1): DBC issues #1163 (metadata.json), #1164 (v1 docs restore), and #1166 (Button `external_link` leakage) were verified 2026-09-20 against `facultyai/dash-bootstrap-components` (state: open; titles match). NiceGUI 3.17.1 release notes record that the 3.17.0 `APIRouter` trailing-slash change broke relative links and was reverted. `ui.run(workers=N)` for `N>1` raises `ValueError` at `nicegui/ui_run.py:287` (“NiceGUI does not support multiple workers yet.”).

---

## 3. Architecture — element implementation strategy

### 3.1 Layering

```
Public Python API
  bs.*  (native snake_case)          dbc.*  (PascalCase compatibility)
                    \                    /
                     \                  /
                Normalization + validation
                     (aliases, enums, children adoption;
                      surface recorded on the instance)
                              |
                    Component contract (manifest)
                              |
              NiceGUI element implementations
     Structural (HTML)  |  Value controls  |  Composites / overlays
                              |
                    Browser adapters (Vue)
     Vue-owned behavior  |  Isolated Bootstrap-plugin bridges (rare)
                              |
                    Shared services
     Assets | Theme | Overlay root | Optional persistence | Diagnostics
                              |
          Pinned Bootstrap CSS in layer(overrides)
          (+ optional Bootswatch builds)
          Selected JS (Popper/positioning only where the adapter needs it)
```

The **component contract** is the organizing unit. Python signatures are real and typed; `**kwargs` is not the public API. The manifest is the source for docs tables, alias handling, and CI.

### 3.2 Alternatives considered (and rejected as the core strategy)

| Approach | Verdict |
|---|---|
| Bootstrap classes on Quasar widgets | Reject. Wrong markup, props, a11y, and CSS. |
| Python functions returning HTML strings | Reject as foundation. Breaks child identity, incremental updates, events, escaping. |
| Custom Vue component for every `span` | Reject as default. Unnecessary frontend surface for `Container`/`CardBody`/`Badge`. |
| Wrap BootstrapVueNext (or similar) wholesale | Not an automatic path to DBC parity; NiceGUI slot/runtime integration unverified. May be reconsidered later for a *single* hard widget, not v1 architecture. |
| Port DBC’s React bundle into NiceGUI | Reject. Wrong runtime; nicegui-react demonstrates the cost of a second UI runtime. |
| Hybrid Python structural + Vue interactive | **Accept.** |

### 3.3 NiceGUI extension mechanics in use

Baseline facts (NiceGUI 3.17.1):

- `ui.element` may wrap a native tag, a registered Vue component, or a Quasar component. This library uses the first two only.
- Construction registers the element with the current client and the active parent slot. Context managers build the tree.
- `.props`, `.classes()`, `.style()` are observable; mutations schedule outbox updates.
- Updates replace element state in the frontend registry (not JSON patches). The outbox coalesces by element ID.
- Adding event listeners after first render can remount the element. **Register standard listeners in `__init__`, not later in update paths.**
- Custom components: `class Foo(ui.element, component="foo.js")` with `dependencies` / `esm` as needed. NiceGUI’s built-in `.vue` processing is lightweight — **interactive frontend is prebuilt** and shipped; users never compile it.
- `ui.html` is for trusted fragments only and does **not** create child Python elements. Not used for user content.
- `ui.add_head_html(..., shared=True)` / `app.add_head_html(...)` affect all page templates. Asset injection is centralized and idempotent. Library CSS is injected as `@import url(...) layer(overrides);` inside a `<style>` tag (or an inline `@layer overrides { ... }` block), never as an unlayered `<link>`.
- Dotted event names are split into type + modifiers. **Never** register `shown.bs.modal` via NiceGUI `.on`. Bridge to `shown` / `hidden` / `toggle` etc.
- `ui.run(workers=N)` for `N>1` is rejected by NiceGUI 3.17.1 (`nicegui/ui_run.py:287`). Do not design as if UI state were multi-worker-safe.
- `ui.refreshable` rebuilds and destroys browser plugin state. Interactive overlays must be **stable instances**.
- NiceGUI 3.17.1 builds an import map with `imports['vue']` pointing at the host Vue 3 runtime (`/_nicegui/{version}/static/vue.esm-browser[.prod].js`). ES modules may `import 'vue'` and resolve to that runtime. `window.Vue` / `globalThis.Vue` also exist. `register_importmap_override(import_name, url)` exists; this library **must not** override `'vue'`.

Internal NiceGUI APIs used by this library are confined to a small `nicegui_bootstrap_components/_host.py` adapter so upgrades touch one file.

### 3.4 Dual API and construction model

#### 3.4.1 Namespaces

Revision note (R1): dual-surface identity is sibling subclasses of a private impl class, with the surface recorded at construction — not one class bound to both names.

```python
# Native (documented default)
from nicegui import ui
from nicegui_bootstrap_components import bs

@ui.page("/")
def page() -> None:
    with bs.scope():  # Mode B island / Reboot anchor; optional in Mode A
        with bs.container():
            with bs.row():
                with bs.col(md=6):
                    name = bs.input(placeholder="Name")
                    bs.button("Save", color="primary", on_click=lambda: ui.notify(name.value))

# DBC compatibility
from nicegui_bootstrap_components import dbc

@ui.page("/compat")
def compat_page() -> None:
    with bs.scope():
        dbc.Container(
            dbc.Row(
                dbc.Col(dbc.Button("Save", color="primary"), md=6),
            ),
            fluid=True,
        )
```

Package root re-exports:

```python
# nicegui_bootstrap_components/__init__.py
from . import bs, dbc, themes, icons
from .assets import setup, StyleMode
from .theme import ThemeController
```

**Chosen dual-surface mechanism.** Each component has one private implementation class (e.g. `_ButtonImpl`) that owns markup, events, and shared validation. Each surface exposes a **sibling subclass** (or a thin factory that instantiates that subclass) which sets `self._surface` to `"native"` or `"compat"` in `__init__` before shared validation runs:

```python
class _ButtonImpl(BootstrapElement):
    component_name = "Button"
    def __init__(self, children=None, *, _surface: str, **props) -> None:
        self._surface = _surface  # "native" | "compat"
        ...

class Button(_ButtonImpl):          # native; bs.Button / bs.button
    def __init__(self, children=None, **props) -> None:
        super().__init__(children, _surface="native", **props)

class DbcButton(_ButtonImpl):       # compat; exported as dbc.Button
    def __init__(self, children=None, **props) -> None:
        super().__init__(children, _surface="compat", **props)
```

`bs.button is bs.Button` (snake_case alias of the **native** class). `dbc.Button is not bs.Button`. `isinstance(dbc.Button(...), bs.Button)` is **False** (siblings, not parent/child). Shared behavior is not duplicated; surface-divergent checks (`type="color"` on Input, public `is_open` on DropdownMenu, `className` warning vs silence, `key` error vs warn, int `debounce`) branch on `self._surface`.

**Tradeoff.** Two types per component instead of one object identity. Ports cannot use `type(x) is bs.Button` as a cross-surface check; they should use the manifest/`component_name` or `isinstance(x, _ButtonImpl)` internally. This is the cost of making OQ21 / 3.4.5 / 4.0.1 enforceable — Python cannot see which module attribute reached a shared class. Wrapper factories that return the impl class with a constructor flag were rejected because `dbc.Button` must remain a type (docs, `isinstance`, mkdocstrings). Compat subclasses of the native class were rejected because they would make every `dbc.Button` an instance of `bs.Button`.

Proposed default naming:

| Surface | Pattern | Example |
|---|---|---|
| Native class | PascalCase, DBC name | `bs.Button` |
| Native factory | snake_case alias of native class | `bs.button is bs.Button` |
| Compat class | PascalCase, distinct type | `dbc.Button` (`DbcButton` internally) |

The compatibility manifest records support **per surface** (`native` / `compat`) for every prop. CI fails if a surface-divergent rule in this TDD lacks a matching manifest field.

#### 3.4.2 Children and reparenting

DBC `children=[...]` builds a nested expression in which **children are constructed before the parent**. NiceGUI attaches on construct. Compatibility therefore requires **adoption**.

Revision note (R1): flatten is recursive only; adoption steals from the ambient slot; mixed text/element children are a documented subset.

Rules (mandatory):

1. Context-manager construction is the native, preferred path. Children constructed inside `with parent:` attach normally. Passing `children=` in that situation is an error.
2. `children=` is supported on the compatibility surface and on native constructors when the parent is **not** used as a context manager at the same call.
3. Adoption **reparents** the given elements onto `self`. Allowed when: same client; not deleted; no cycle; and the child’s current parent is the **ambient slot’s parent at the start of this constructor** (typically the page content slot or an enclosing context-manager element). That is exactly the nested-expression case: `dbc.Row(dbc.Col(...))` constructs `Col` first (it attaches to the ambient slot), then `Row` steals it. Do not require a “just-created wrapper.” Stealing from an unrelated long-lived parent that the user already placed elsewhere in the tree raises `ChildrenError`.
4. Strings, numbers, and `None` in `children` are handled as in the representation rules below. Lists/tuples are **flattened recursively**; `None` is dropped; unknown types raise `TypeError`. (There is no “one-level only” flatten.)
5. Duplicate ownership raises `ChildrenError`. Moving an element later uses NiceGUI’s move APIs through `_host`.
6. Order of `children` is preserved.
7. Native context-manager vs DBC nested-tree may be mixed across a page, not inside a single constructor call.

Sketch:

```python
def _normalize_children(children: object) -> list[object]:
    if children is None:
        return []
    if isinstance(children, (str, int, float, ui.element)):
        return [children]
    if isinstance(children, (list, tuple)):
        out: list[object] = []
        for c in children:
            out.extend(_normalize_children(c))
        return out
    raise TypeError(f"Unsupported child type: {type(children)!r}")
```

Text children are never assigned to `innerHTML`.

**Interleaved text / element children (representation).** NiceGUI elements expose a default-slot **text** plus an ordered list of element children. That cannot represent `["Messages ", Badge("4")]` as a single text slot without reordering. Wrapping every text run in a box-generating element would break Bootstrap child/sibling selectors that 4.0.6 promises to preserve (`.btn-group .btn + .btn`, `.input-group > .form-control`, `.input-group > :not(:first-child)`). `display: contents` does **not** fix this: selectors match the element tree, not the box tree.

Supported subset:

| Parent kind | Allowed children | Representation |
|---|---|---|
| **Selector-sensitive grouping** (`InputGroup`, `ButtonGroup`, `ListGroup`, `CardGroup`, `Row` when treating columns as direct children) | Element children only | No text wrappers. A non-empty text run raises `ChildrenError` with a hint to wrap in a component. Preserves `>` / `+` / `:first-child` contracts. |
| **Phrasing / content** (`Button`, `NavLink`, `Badge`, `Alert`, `Label`, `ModalTitle`, `DropdownMenuItem`, `CardLink`, `NavbarBrand`, …) | Mixed text and elements | Each consecutive text run (str/int/float) becomes one `<span class="ngbs-text">` element, in order, interleaved with real children. These parents do not rely on Bootstrap adjacent-sibling combinators among their children. |
| **Text-only** (no element children) | A single concatenated text slot | NiceGUI default-slot text; **no** extra span. Matches typical `<button>Save</button>` markup. |

Do not concatenate interleaved runs into one slot (that reorders relative to elements). Do not use `innerHTML`.

#### 3.4.3 Identity

| ID | Owner | Purpose |
|---|---|---|
| NiceGUI element id | Framework | Outbox, frontend registry. Never overwritten. |
| `html_id` | NiceGUI | DOM `id` used by NiceGUI lookup. Do not casually replace. |
| Public `id` prop (DBC) | Library | Application-facing identity for tests, overlay targets, and docs. Stored as a library prop. If the caller needs a DOM id, set it through a dedicated `dom_id` / passthrough that is applied only when it cannot clash with NiceGUI’s lookup (see Open question 3). |

Overlay targets (`Tooltip.target`, `Popover.target`) accept **element references** natively. Compatibility `target` as a string id is resolved via a **per-client registry** of public ids, not by guessing NiceGUI internals.

Do not implement Dash pattern-matching dict/tuple ids.

#### 3.4.4 Props, aliases, styles

Revision note (R1): no keyword-only separator on `dbc.*`; numeric `style` values follow React/DBC px rules; surface-specific alias warnings.

Shared normalization (applied by `BootstrapElement.__init__`):

- Canonical: `class_name: str | None = None`, `style: dict[str, str] \| None = None`.
- Deprecated alias: `className` accepted; if both `class_name` and `className` are nonempty, **`class_name` wins** (DBC). If both nonempty and unequal: **native** surface emits `DeprecationWarning` once per element; **compat** surface is silent (DBC).
- Region styles keep DBC names: `dialog_style`, `content_style`, `backdrop_style`, `spinner_style`, `toggle_style`, plus camelCase aliases `dialogStyle`, `contentStyle`, `spinnerClassName`, etc. where DBC 2.0.4 still accepts them.
- `style` dictionaries: keys as CSS properties. **Numeric values are px-ified to match React/DBC** (`{"width": 100}` → `width: 100px`), except a fixed allow-list of unitless properties (`opacity`, `z-index`, `font-weight`, `line-height`, `flex`, `flex-grow`, `flex-shrink`, `order`, `zoom`, `animation-iteration-count`, and the other React unitless keys). Strings pass through unchanged. Unknown keys pass through to inline style on the **declared styling target node** only.
- `.classes()` / `.style()` remain available and compose with `class_name` / `style`. Library-owned classes live in a reserved set and are re-applied after user class mutations if the user strips a required structural class (e.g. `btn`). Implementation: structural classes stored separately and merged on render.
- Conflicting aliases that would map to different nodes raise `PropConflictError`.
- HTML-like names stay lowercase where DBC does: `autocomplete`, `readonly` (not rewritten to `read_only` on the compatibility surface). Native surface may additionally accept `read_only` as an alias of `readonly` (extension, documented).

Keyword-only constructors on the **native** surface (after optional children / label). **Compatibility constructors match DBC’s generated signature shape:** optional `children` first, remaining props positional-or-keyword. Dash-generated classes accept positional arguments (`@_explicitize_args` exists because positional passing works). Do **not** insert a keyword-only separator after `id` on `dbc.*`.

#### 3.4.5 Events vs Dash counters

| DBC | Native | Compat |
|---|---|---|
| `n_clicks` | `on_click: Callable` | both: handler **and** incrementing `n_clicks` (read-only observable) |
| `n_submit`, `n_blur` | `on_submit`, `on_blur` | both |
| `value` + implicit `setProps` | bindable `.value` + `on_change` | `.value` writable; `on_change` fires with the new value |
| no public open state (`DropdownMenu`) | optional extension `is_open` on native only (`bs.DropdownMenu` accepts; `dbc.DropdownMenu` raises `UnsupportedPropError`) | no public `is_open` |
| Dash `persistence*` | optional `persist=` helper (Section 3.9) | accepted but **adapted**; see 4.0.8 |

Disabled controls do not fire click counters (DBC Button: disabled does not increment `n_clicks`).

Native handlers are registered at construction. Compat counters are Python integers on the element, updated when the frontend event arrives, then user handlers run.

Payloads are compact (no raw DOM events unless a documented `js_handler` is used). Hover/move/position stay in the browser.

### 3.5 Base types

Revision note (R1): value controls inherit NiceGUI `ValueElement`; frontend contract is `model-value` + `update:modelValue`.

```python
# Conceptual sketch — implementation in nicegui_bootstrap_components/core.py
# ValueElement: nicegui.elements.mixins.value_element.ValueElement

class PropConflictError(ValueError): ...
class ChildrenError(ValueError): ...
class UnsupportedPropError(TypeError): ...  # Dash-only or wrong-surface props used meaningfully

class BootstrapElementMixin:
    """Contract, adoption, public ids, reserved classes. Not an element by itself."""
    component_name: str                    # manifest key, e.g. "Button"
    styling_target: str                    # "root" | "dialog" | ...
    reserved_classes: tuple[str, ...]
    _surface: str                          # "native" | "compat" — set by public subclass

class BootstrapElement(BootstrapElementMixin, ui.element):
    """Structural or hybrid Bootstrap element."""
    def __init__(self, children=None, *, id=None, class_name=None, className=None,
                 style=None, **compat_props) -> None: ...
    def _apply_contract(self, props: dict) -> None: ...
    def _adopt(self, children) -> None: ...
    def _set_public_id(self, public_id: str | None) -> None: ...

class BootstrapValueElement(BootstrapElementMixin, ValueElement):
    """Form control with .value and on_change.

    Inherits NiceGUI ValueElement (value property, bind_value / bind_value_from /
    bind_value_to, on_value_change, loopback protection). Do not invent a second
    binding system. If the diamond with ui.element is unclean, keep this MRO
    (ValueElement already subclasses Element) and apply BootstrapElementMixin
    only; _host.py adapts if ValueElement moves.
    """
    # Frontend contract for every V value control:
    #   - accept prop `model-value`
    #   - emit `update:modelValue` with the new value
    # NiceGUI ValueElement already listens for update:modelValue.

class OverlayElement(BootstrapElement):
    """Desired vs actual visibility; overlay-root registration."""
    is_open: bool                          # or is_in for Fade
    phase: str                             # closed|opening|open|closing
```

If a future NiceGUI version makes the mixin MRO fail, copy **only** the published ValueElement subset (`value`, `set_value`, `bind_value`, `bind_value_from`, `bind_value_to`, `on_value_change`, loopback guard) rather than a new API — still through `_host.py`.

### 3.6 Per-component implementation decision record

Legend:

- **P** — Pure Python `ui.element("tag")` (or subclass) emitting Bootstrap markup. No custom JS.
- **V** — Custom Vue component (prebuilt). Vue owns behavior and DOM class transitions.
- **H** — Python composite: P children plus a small V controller on the root.
- **Plug** — Vue wrapper + isolated Bootstrap plugin instance on a designated inner node. Allowed only with the lifecycle rules in 3.7.

| Component | Impl | Rationale |
|---|---|---|
| Container, Row, Col, Stack | P | Grid is markup + classes. |
| Card, CardBody, CardHeader, CardFooter, CardGroup, CardImg, CardImgOverlay, CardLink | P | Structural. |
| Badge | P | Classes; optional `<a>`/`<span>`. |
| ListGroup, ListGroupItem | P | Structural; actionable items are links/buttons. Tag fixed at `__init__`. |
| Table | P | Semantic `<table>`; `from_dataframe` builds cells in Python. |
| Progress | P | Width/ARIA from Python props; CSS animation. |
| Placeholder | P | CSS skeleton. |
| Form, FormFloating, FormText, FormFeedback, Label | P | Semantic HTML. |
| InputGroup, InputGroupText | P | Structural grouping. |
| ButtonGroup | P | Structural. |
| Nav, NavItem, NavLink | P | Structural + active classes. |
| Navbar, NavbarBrand | P | Structural. |
| NavbarToggler | H | Button markup + collapse controller wiring. |
| NavbarSimple | P/H | Composition of the above, not a second navbar. |
| Breadcrumb | P | Generated from `items` or children. |
| Button | P or V | Native `<button>`/`<a>` is enough if click is a NiceGUI event. Use V only if we need to prevent remount issues; **proposed default: P** with construction-time `.on("click")`. |
| Input, Textarea | V | Debounce, composition events, selection preservation, numeric None. |
| Select | V | Native `<select>`, string value contract. |
| Checkbox, Switch, RadioButton | V | Bindable boolean / grouping. |
| Checklist, RadioItems | H | Python options renderer + V group value. |
| DropdownMenu, DropdownMenuItem | V | Placement, keyboard, outside click; **internal** open state. |
| Tabs, Tab | H/V | Keyboard, `active_tab`, generated ids. |
| Pagination | P/H | Generated items; clicks update `active_page`. |
| Alert | P if not dismissible; V if dismissible | Transition + dismiss sync. |
| Spinner | P | CSS animation; explicit `loading` analogue — no Dash loading probe. |
| Accordion, AccordionItem | V | Coordinated disclosure, `always_open` shape change. |
| Collapse | V | Height transition, desired vs actual. |
| Fade | V | Opacity transition; `is_in`. |
| Modal + Header/Title/Body/Footer | H/V | Focus, backdrop, scroll lock, `is_open`. Prefer **V-owned** dialog; do not let Bootstrap Modal plugin and Vue both write classes. |
| Offcanvas | V | Placement, backdrop, scroll; shared overlay services. |
| Toast | V | Timer, autohide, live region. |
| Tooltip | Plug or V | Positioning. **Proposed default: V using Floating UI or Popper, Vue-owned**, to avoid Bootstrap Tooltip `innerHTML` and plugin/Vue fights. |
| Popover, PopoverHeader, PopoverBody | V | Rich children must remain a Vue/NiceGUI tree — **never** serialized into plugin HTML. |
| Carousel | V | Interval, pause, `active_index`, item replacement mid-transition. |
| Scope (native extension) | P | Mode B island / Reboot anchor. Not a DBC export. |

**Bootstrap’s own JS plugins are not the default.** DBC itself uses React-Bootstrap, not Bootstrap’s jQuery-style plugins. Matching DBC is therefore **reimplement behavior on Vue**, not “call `bootstrap.Modal.getOrCreateInstance` for everything.”

Plugin bridges (if a spike shows Vue positioning is insufficient) are allowed only for Tooltip *plain-text* mode. Popover with components stays Vue-owned. The prototype (phase 2) must choose V vs Plug for Tooltip and freeze it.

### 3.7 Browser behavior and Python callbacks

#### 3.7.1 Ownership rule

Bootstrap warns that its JavaScript and Vue must not both mutate the same DOM. For every interactive component:

- Vue owns the component tree and child content.
- If a plugin is used, it owns a **named inner node** only (e.g. empty positioning sentinel), never the slot that contains NiceGUI children.
- `data-bs-toggle` global auto-init is **disabled** for library components (no double init).
- Library wrappers never also add Bootstrap data-api attributes that would auto-construct a second instance.

#### 3.7.2 Desired vs actual state

Overlays and disclosure components store:

```text
desired  (is_open / is_in / active_item / active_tab / active_index)
phase    (closed | opening | open | closing)   # overlays/collapse/fade
revision (monotonic int)
```

Python `.open()` / setting `is_open=True` sets **desired** and sends a command. It does **not** imply the animation finished. Frontend coalesces rapid commands (last desired wins). Calls during a transition are queued, not dropped on the floor without reconciliation (Bootstrap plugins may ignore calls during transition — the adapter must retry on `hidden`/`shown` equivalents).

Events:

| Library event | Meaning |
|---|---|
| `show` / `hide` | Transition started (requested or user). |
| `shown` / `hidden` | Transition completed. |
| `change` | Value / selection / page / tab / accordion item committed. |
| `dismiss` | User dismiss (close button, Esc, static-backdrop click ignored, autohide). |
| `click` | Activation. |

Each event payload:

```python
@dataclass(frozen=True)
class BsEvent:
    name: str
    cause: str          # "api" | "user" | "escape" | "backdrop" | "timer" | "keyboard"
    desired: object
    actual: object
    revision: int
```

Python callbacks cannot cancel a synchronous browser event after the round trip. **Guarded close** (e.g. “confirm before modal close”):

1. Native extension: `prevent_close=True` makes the frontend *not* close on Esc/backdrop; it emits `close_request`.
2. Server calls `.close()` if allowed.
3. This is an **extension**, off by default, so DBC `is_open` dismissal still closes immediately like DBC.

#### 3.7.3 Wiring map for JS-heavy widgets

**Modal**

- Vue dialog: `role="dialog"`, `aria-modal="true"`, labelled by `ModalTitle` id.
- `is_open` desired flag.
- Backdrop node rendered in the **overlay root** (Section 3.8), not inside a transformed parent.
- `backdrop=True`: click backdrop → desired False + `dismiss` cause=`backdrop`.
- `backdrop="static"`: click backdrop does not close; optional shake class.
- `backdrop=False`: no backdrop, no click-outside.
- Keyboard: Esc closes unless disabled (map DBC’s keyboard prop once extracted).
- Focus: trap while `phase in {opening, open}`; restore previously focused element on `hidden`.
- Body scroll lock on `show`, restore on `hidden` even if the element is deleted mid-transition.
- `enforceFocus` (camelCase preserved on compat): when True (DBC default — confirm in manifest extract), keep focus inside. Native alias `enforce_focus`.
- Python: `on_show`, `on_shown`, `on_hide`, `on_hidden`, `on_dismiss`; setting `is_open` from Python does not increment a fake counter.
- Deletion while open: adapter disposes backdrop, unlocks scroll, restores focus, no leaked listeners.

**DropdownMenu**

- Vue-controlled; **no public `is_open` on dbc surface** (`dbc.DropdownMenu(is_open=...)` → `UnsupportedPropError`). Native class accepts bindable `is_open` + `on_toggle` as an extension.
- Toggle click / keyboard (Enter/Space/Arrow) opens; Esc, outside click, tab-away close.
- Direction `down|start|up|end` → Bootstrap class names (`dropup`, `dropend`, …).
- `menu_variant` `light|dark`.
- Positioning: CSS first; flip/overflow via Floating UI in the Vue component if needed. Menu rendered in overlay root when it would clip (`in_navbar` / overflow cases — see Open question 4; proposed default: render in overlay root when `in_navbar` or `strategy="fixed"`, else inline for simplicity).
- Item click: for `toggle=True` items, close after click (Bootstrap default). Headers/dividers not focusable in the item list.

**Collapse / Accordion**

- Vue height transition (`overflow: hidden`; height from `scrollHeight` to `0`).
- `Collapse.is_open`; `Accordion.active_item`.
- Reduced motion: skip duration if `prefers-reduced-motion: reduce`.
- Accordion single-open: opening one closes the previous unless `always_open`.
- `always_open=True`: `active_item` is a **list of ids**; otherwise a **scalar id** (or None if `start_collapsed`).
- Default: first item selected unless `start_collapsed`.
- Unmount during transition: cancel rAF/listeners.

**Fade**

- `is_in` (not `is_open`). Opacity transition. Enter/exit timing props from DBC declaration (extract). Completes to unmount or `display:none` as specified by DBC `unmount_on_exit` analogue if present — extract; proposed default: keep in DOM unless a DBC prop says otherwise.

**Offcanvas**

- Same overlay service as Modal (backdrop, scroll, focus) with placement `start|end|top|bottom` and responsive `*-lg` variants from DBC props (extract).
- Distinct from Modal: does not use `role="dialog"` in all Bootstrap versions the same way — follow Bootstrap 5.3 offcanvas ARIA.

**Toast**

- DBC default: **open, not dismissible, no timer unless `duration` supplied**. Do not treat as NiceGUI `ui.notify`.
- Dedicated toast container (overlay root region) if `position` requires it.
- `duration` in ms → timer; autohide emits `dismiss` cause=`timer` and sets visibility False.
- Live region: `role="status"` / `aria-live="polite"` by default; `role="alert"` only if a documented `autohide` urgency extension is used (do not over-announce every toast).
- No DBC `color` prop (see 4.16).

**Tooltip**

- Target: element ref (native) or public id (compat).
- Triggers: hover + focus default (extract DBC). Delay show/hide.
- Content is **text** (escaped). No HTML unless a documented `is_html` exists in DBC — if DBC allows HTML, still default to text; HTML only for trusted strings and never for NiceGUI children.
- Cleanup on target deletion.
- `aria-describedby` linkage.

**Popover**

- Vue overlay with slots for `PopoverHeader` / `PopoverBody` as real child components.
- Do not stringify children into Bootstrap’s `data-bs-content`.
- Keyboard: Esc closes. Tab is **not** fully trapped (Bootstrap does not manage this); document that interactive popovers are a limited a11y surface.

**Carousel**

- `items: list[dict]` — not child `CarouselItem` components (those must not be exported).
- Zero-based `active_index`, default 0.
- `interval`, `controls`, `indicators`, `slide`; pause on hover if DBC does (extract).
- When `items` is replaced mid-transition: cancel transition, clamp index, snap (no leftover interval).
- Persistence analogue on `active_index` if enabled.

**Spinner loading analogue**

- DBC coordinates with Dash loading state via `window.dash_component_api`. **Out of scope.**
- Replacement: `loading: bool | None = None` and wrapping children. `display: auto|show|hide` maps to: auto = show spinner when `loading` True (or when children empty and loading True); show/hide force.
- `delay` / hide delay honored with frontend timers.
- `fullscreen` renders in overlay root.
- Color: semantic names **or** arbitrary CSS color (DBC Spinner).
- Type: `border` | `grow`.

#### 3.7.4 Python → frontend method calls

Prefer props (`is_open=True`) over `run_javascript` string interpolation. If a method is needed:

```python
await modal.run_method("setDesiredOpen", True)
```

Never interpolate user content into JS strings. No `innerHTML` for untrusted content.

Reconnection: NiceGUI may replay or reload. Adapters **reconcile to current desired state**, not replay historical animation commands. On client delete, dispose plugins, timers, MutationObservers, popovers, backdrops.

### 3.8 CSS conflict management with Quasar / Tailwind

Revision note (R1): library CSS is assigned to pre-declared `layer(overrides)`; Reboot `html`/`body` map to the scope-anchor, not `.ngbs html`/`.ngbs body`.

NiceGUI 3.17.1 `templates/index.html` contains **exactly** this in `<style>` (verified against the installed package, 2026-09-20):

```
@layer theme, base, quasar, nicegui, components, utilities, overrides, quasar_importants;
@import url(".../static/fonts.css") layer(base);
@import url(".../static/quasar.unimportant.prod.css") layer(quasar);
@import url(".../static/quasar.important.prod.css") layer(quasar_importants);
@import url(".../static/nicegui.css") layer(nicegui);
```

Cascade facts used by this library:

- For **normal** (non-`!important`) declarations: unlayered wins over layered; among layers, later-listed layers win.
- For **`!important` declarations, layer order is inverted**: among layered importants, an **earlier-listed** layer wins over a later-listed layer. Unlayered `!important` loses to layered `!important`.
- Therefore `!important` in `layer(overrides)` outranks `!important` in `layer(quasar_importants)` (overrides is listed *before* `quasar_importants`). Specificity cannot make unlayered `!important` beat layered `!important`.
- Quasar ships `.text-primary` / `.bg-primary` with `!important` in `quasar.important.prod.css` → `layer(quasar_importants)`.
- Tailwind’s `.collapse` is `visibility: collapse`, which fights Bootstrap’s disclosure `.collapse`. Tailwind (and user CSS) is unlayered by default, so its **normal** rules beat our layered **normal** rules; conflict fixes must use `!important` inside `layer(overrides)` so they beat unlayered Tailwind *and* Quasar importants.
- Quasar defines `.row` and column-like rules. NiceGUI adds container spacing.
- Overlay z-index scales differ (Bootstrap ~1000 vs Quasar menus 6000 / tooltips 9000 / notifications 9500).

**Injection (Mode A and Mode B).** Never register library CSS as an unlayered `<link>` or unlayered `<style>` body. Use `app.add_head_html` / `ui.add_head_html`:

```python
# Shared, idempotent — AssetManager
ui.add_head_html(
    f'<style>@import url("{href}") layer(overrides);</style>',
    shared=True,
)
# Small host/compat rules may be inlined:
ui.add_head_html("<style>@layer overrides { /* ngbs-host / ngbs-compat */ }</style>", shared=True)
```

Do not introduce a new layer after `quasar_importants` (a last-listed layer would be *weakest* for `!important`). Do not assign library sheets to `quasar_importants`.

**Unlayered user CSS and CDN Bootstrap (tradeoff, explicit).** User-level code (`ui.add_css`, inline `style=`, third-party `<link>`, raw CDN Bootstrap) is unlayered by default.

- Unlayered **normal** user rules **win** over library **normal** rules in `overrides`. Authors can tweak spacing/colors without `!important`.
- Unlayered **`!important` user rules lose** to library `!important` in `overrides`. Authors who need to override a Bootstrap/Quasar-beating utility must inject into the same layer: `ui.add_head_html('<style>@layer overrides { .ngbs .text-primary { color: ... !important; } }</style>')`.
- Therefore Mode A **must not** load CDN Bootstrap as a raw `<link>` (unlayered Bootstrap `!important` loses to Quasar). Mode A CDN uses `@import url(...) layer(overrides);` as well. Mode B never uses unscoped upstream CDN (9.5).

This tradeoff is accepted: beating Quasar importants is the coexistence gate; the escape hatch for app overrides is `@layer overrides`.

#### 3.8.1 Two supported modes

**Scope-anchor vs per-component marker.** Class `ngbs` is a **scope-anchor**, not a per-component marker. It is applied only to:

1. `bs.scope` (native extension; Mode B island wrapper, tag `div`),
2. `#ngbs-overlay-root` (also `ngbs-overlay`).

Individual components (`Button`, `Col`, …) do **not** each carry `ngbs`. Bootstrap selectors are rewritten against the ancestor anchor (`.ngbs .btn`), so child/sibling combinators inside an island still match.

**Mode B selector map** (mandatory; the scoper / PostCSS prefixer must implement this, not naive “prefix every selector with `.ngbs `”):

| Source selector | Rewritten to | Why |
|---|---|---|
| `html`, `body`, `:root` | `.ngbs` | Reboot typography, background, margin, and `--bs-*` variables apply to the **island wrapper**, once. Never emit `.ngbs html` or `.ngbs body` (those match nothing). Never emit `html`/`body` rules onto every component root. |
| `html <x>`, `body <x>` | `.ngbs <x>` | Descendant of the anchor. |
| any other selector `S` | `.ngbs S` | Component rules stay relative to the island. |
| `@keyframes`, `@font-face` | unchanged | Not prefixed. |

Mapping `body` → `.ngbs` is correct **only because** `.ngbs` is the single island wrapper, not every widget. Mapping it onto every component would apply `margin: 0` and body background to each button.

**Mode A — Bootstrap-first (recommended for apps that are “a Bootstrap app on NiceGUI”)**

- Caller runs NiceGUI with `tailwind=False` (documented, **not** implicit on import).
- Library injects the **unscoped** pinned Bootstrap (or Bootswatch) stylesheet **into `layer(overrides)`**, plus a small `ngbs-host.css` (also `layer(overrides)`) that:
  - Neutralizes remaining NiceGUI content padding on `bs.container` roots where it would break grid.
  - Defines overlay z-index using Bootstrap’s scale.
  - Does not attempt to restyle Quasar widgets.
- Reboot `html`/`body` apply to the real document (unscoped). `bs.scope` is optional and harmless.
- Quasar widgets on the same page are **best-effort only**; documented as unsupported for visual identity. Functional coexistence tests still run so we do not crash.
- Color utilities (`!important`) in `layer(overrides)` beat `quasar_importants`.

**Mode B — Mixed-page Bootstrap scope (default if the host still uses Tailwind/Quasar styling)**

- Authors wrap each Bootstrap island in `bs.scope()` (class `ngbs`). Overlay portal root is also a scope-anchor.
- CSS is a **scoped build** using the selector map above. `--bs-*` live on `.ngbs` / `.ngbs-overlay`, not unconditionally on `:root`.
- Overlays portal to `#ngbs-overlay-root` which has `ngbs ngbs-overlay` and the same `data-bs-theme`.
- **Inside `.ngbs`**, a compatibility layer **in `layer(overrides)` with `!important` where needed**:
  - Re-asserts Bootstrap `.collapse { visibility: visible; }` (and collapsing/show rules) so Tailwind’s unlayered `.collapse` does not win.
  - Re-asserts Bootstrap color utilities for `.ngbs .text-primary` etc. so they beat Quasar’s `quasar_importants` utilities **inside the scope only**.
  - Does not rewrite Bootstrap *class names* (users still write `btn btn-primary`). Prefixing all classes was rejected: it would break Bootswatch and user CSS.
- Nesting **Quasar widgets inside `.ngbs`** is not supported (they will pick up Bootstrap resets). Nesting **`.ngbs` inside Quasar layout** is the intended mixed pattern.
- Shadow DOM is **not** used in v1 (slots, overlays, utilities, NiceGUI children).
- Debug: constructing a library component outside any `.ngbs` ancestor while Mode B is active logs a one-time hint; it is not auto-wrapped (auto-wrap would break `>` selectors across the wrapper).

`setup()` API:

```python
from nicegui_bootstrap_components import setup, StyleMode, themes

setup(
    mode=StyleMode.MIXED,          # or StyleMode.BOOTSTRAP_FIRST
    theme=themes.BOOTSTRAP,        # or themes.FLATLY, or a local URL
    color_mode="auto",             # "light" | "dark" | "auto"
)
```

`setup()` is a **module-level / process-level** call (examples call it at import time, before any page exists). It:

- Registers CSS/JS once (idempotent) via `add_head_html(shared=True)` using `@import ... layer(overrides)`.
- Stores **defaults** for mode, theme, color_mode, icons on `AssetManager`.
- Does **not** bind to a client.

Calling `setup()` twice with conflicting **mode** (scoped vs unscoped asset set) raises, process-wide. Theme and `color_mode` at `setup()` are defaults for new clients; they are not a process-global mutable theme that leaks across users. Per-client changes go through `ThemeController` (3.8.1 lifecycle / 5.3).

#### 3.8.2 Overlay root and z-index policy

- Create `#ngbs-overlay-root` on first overlay mount (body child), classes `ngbs ngbs-overlay`.
- Mode A: z-index follows Bootstrap 5.3 (verify against the pinned Bootstrap version’s `_variables.scss` at implementation; use the pinned values as source). Expected 5.3 scale:

| Token | Typical z-index |
|---|---|
| dropdown | 1000 |
| sticky | 1020 |
| fixed | 1030 |
| offcanvas-backdrop | 1040 |
| offcanvas | 1045 |
| modal-backdrop | 1050 |
| modal | 1055 |
| popover | 1070 |
| tooltip | 1080 |

- Mode B: place the overlay root as a top-level sibling with `z-index: 5000` (below Quasar menus ~6000 / tooltips ~9000 / notifications ~9500, above typical content). Bootstrap’s internal scale then applies *inside* that stacking context.
- **Mixing a Quasar dialog and a Bootstrap modal is unsupported.** Mixing a Quasar menu/tooltip with a Bootstrap dropdown/tooltip/offcanvas is also unsupported: Mode B’s overlay root at 5000 sits *below* Quasar menus (6000), so a portaled Bootstrap dropdown loses to a Quasar menu. Document “pick one overlay system.” Toast vs `ui.notify` stacking is undefined if both used; prefer one system.

#### 3.8.3 Tailwind `.collapse` specific fix

Ship `ngbs-compat.css` inside `@layer overrides`. Applied inside `.ngbs` / `.ngbs-overlay` only; `!important` is required to beat unlayered Tailwind:

```css
@layer overrides {
  .ngbs .collapse:not(.show) {
    visibility: visible !important; /* cancel Tailwind visibility: collapse */
    display: none !important;
  }
  .ngbs .collapse.show {
    visibility: visible !important;
    display: block !important;
  }
  .ngbs .collapsing {
    visibility: visible !important;
  }
}
```

Exact `display` values must match Bootstrap’s component (collapse vs navbar vs width). Tests: a `bs.collapse` panel must not remain `visibility: collapse` when shown.

#### 3.8.4 NiceGUI layout defaults

`bs.container` / `bs.row` / `bs.col` must not inherit NiceGUI flex-gap padding in a way that breaks the 12-column grid. `ngbs-host.css` (in `layer(overrides)`) resets `gap`/`padding` on those roles to Bootstrap’s. Do not globally reset NiceGUI’s `q-page` in Mode B.

### 3.9 Shared services

**Assets.** `AssetManager` registers CSS/JS hashes, versions, and mode. Duplicate registration is a no-op. Default: bundled files in `nicegui_bootstrap_components/static/`. CDN is opt-in with pinned version + integrity (Section 9). Do not load the full Bootstrap JS bundle if adapters are Vue-native. All library stylesheets go through the `layer(overrides)` injection path in 3.8.

**Theme.** `ThemeController` (Section 5): **per-client**, not process-global. Writes `data-bs-theme` on the scope-anchor and overlay root. Watches Quasar `body--dark` when `mode="auto"` so Bootstrap follows the *resolved* browser theme, not only the Python preference.

**ThemeController lifecycle and stylesheet-swap (mandatory).**

Revision note (R1): module-level `setup()` registers assets; `ThemeController.for_client()` binds page-lifetime state and swaps stylesheets per client.

1. `setup()` at import registers shared layered imports for the **default** theme and records defaults. No page exists yet.
2. On first library use in a client (first `bs.scope` / overlay / `ThemeController.for_client()` inside a `@ui.page`), bind a controller on that NiceGUI `client` (store in client extras via `_host`). Page-lifetime: discarded when the client is deleted.
3. **Color mode** is an attribute (`data-bs-theme` on `.ngbs` / overlay root), updated in the client’s document. No stylesheet swap.
4. **Theme file swap** (Bootswatch ↔ Bootstrap) is per-client: `ui.add_head_html(..., shared=False)` injects a client-owned `<style id="ngbs-theme-client">@import url("…") layer(overrides);</style>`. `set_theme()` replaces that tag via a small JS helper (`document.getElementById('ngbs-theme-client')` remove + insert) so other users on the same process keep their sheet. The shared default import remains as fallback until the client override exists.
5. Examples construct the controller **inside the page function** (or rely on lazy bind). Never store color mode on a module global.

**Persistence (optional analogue).** DBC persistence uses Dash’s store (`local` / `session` / `memory`) for selected props (`value`, `active_item`, `active_tab`, `active_index`). v1 ships `persist="off"|"local"|"session"` as an **adapted** helper using `window.localStorage` / `sessionStorage`. **Requires a public `id`** (`persist != "off"` without `id` → `ValueError`). Storage key `ngbs:{id}:{prop}` (OQ15). Memory persistence is in-element only (already the default). This is **not** Dash persistence (no `persistence_type` on a hidden Dash store). Documented as adapted. Default `off` so nothing is written unless opted in.

**Restore semantics (mount):**

- Read storage before first user interaction. If a valid value exists, apply it as the initial `value` / `active_*`.
- Restore **does not** fire `on_change` / increment counters.
- Restore **does not** write back to storage (no restore→set→persist loop).
- Subsequent user or API commits write to storage.
- Missing key: constructor default. Invalid JSON / wrong type: ignore, keep default, debug log once.
- Same-tab `storage` events that match the current value are ignored.

**Diagnostics.** In NiceGUI debug, log double-init, missing overlay root, Mode B component outside `.ngbs`, and class-conflict hints once.

### 3.10 Frontend packaging

```
frontend/
  src/           # Vue SFCs / TS for V components
  dist/          # built ES modules, consumed by the Python package
styles/
  scss/          # Bootstrap source + scoping wrapper (selector map in 3.8.1)
  dist/          # ngbs.css, ngbs-bootswatch-*.css, ngbs-compat.css
```

Build in CI. Wheel contains `frontend_dist/` and `styles/dist/` only. Vue components are ES modules that **externalize `vue`** to the host NiceGUI Vue 3 runtime (same constraint DBC used by externalizing React). NiceGUI 3.17.1’s import map provides `'vue'`; `window.Vue` / `globalThis.Vue` exist as well. Do not bundle Vue. Do not call `register_importmap_override('vue', ...)`.

Revision note (R1): host import map for `'vue'` is verified in NiceGUI 3.17.1; L2/L3 still assert `import('vue')` resolves (guard against future host changes).

NiceGUI custom-component registration:

```python
class BsModal(OverlayElement, component="modal.js", dependencies=["static/ngbs-compat.css"]):
    ...
```

Exact dependency wiring follows NiceGUI 3.17.1’s `component=` / `dependencies=` / `esm=` (adapter in `_host.py`).

### 3.11 Schema-first contract (mandatory before coding widgets)

DBC 2.0.4 Python classes are generated from React `propTypes`. This TDD records every contract the research established. Remaining per-prop details (complete lists, exact defaults, nested dict shapes) are **extracted once** from the 2.0.4 tag into `contracts/dbc-2.0.4.json` (phase 1) using this procedure — not ad-libbed:

1. Check out `facultyai/dash-bootstrap-components` tag `2.0.4`.
2. Read exports from `dash_bootstrap_components/__init__.py` / `src/index.js` (66 names).
3. For each generated class in `dash_bootstrap_components/_components/`, record `__init__` parameters, defaults, and docstring fields.
4. Cross-check `src/components/**/*.js` propTypes for enums and nested shapes.
5. Record removed names from `__init__.py` reject list.
6. Mark Dash-only props (`loading_state` if any, persistence trio, `key` as React key) with disposition.
7. Freeze the JSON in-repo. Implementation and docs **must not** add props that are not in the JSON without an “extension” flag **and** a per-surface support field.

Manifest per-prop shape (minimum):

```json
{
  "name": "debounce",
  "dbc_type": "boolean",
  "default": false,
  "surfaces": {
    "compat": { "support": "supported" },
    "native": { "support": "extension", "notes": "also accepts int milliseconds" }
  }
}
```

Until that JSON exists, implementers use Section 4 plus this disposition policy:

| Kind | Action |
|---|---|
| Prop documented in this TDD | Implement as specified. |
| Prop in 2.0.4 generated signature, portable | Implement; add to manifest. |
| Prop that exists only for Dash loading/persistence/link routing | Adapted or unsupported per 4.0.8. |
| Historical removed prop | Reject with `TypeError` mentioning the 2.0 removal. |
| React-Bootstrap-only prop not exported by DBC | Do not implement. |
| Native-only extension | `support: extension` on native; `UnsupportedPropError` on compat if passed. |

---

## 4. Component designs — full DBC 2.0.4 inventory

### 4.0 Cross-cutting contracts

#### 4.0.1 Shared constructor fields

Unless a component’s DBC schema omits them, every visual component accepts:

| Prop | Native | Compat | Notes |
|---|---|---|---|
| `children` | yes | yes | See 3.4.2. |
| `id` | public id | public id | Not NiceGUI internal id. |
| `class_name` | yes | yes | Preferred. |
| `className` | deprecated alias | deprecated alias | Nonempty `class_name` wins. Warning only on native. |
| `style` | dict | dict | Target = root unless specified. Numbers px-ified except unitless allow-list (3.4.4). |
| `key` | unsupported | unsupported | Dash/React list key. **Compat:** `UnsupportedPropError`. **Native:** warn once per process, ignore. |

There is no separate “compat strict mode” flag; the compat surface is always strict for unsupported/extension props.

#### 4.0.2 Color vocabulary

Common semantic colors: `primary`, `secondary`, `success`, `info`, `warning`, `danger`, `light`, `dark`.  
Additional: `link` (Button), arbitrary CSS color (Spinner, and DropdownMenu where DBC allows). **Button maps `color` to Bootstrap `variant` / `btn-*`; it does not accept arbitrary hex unless DBC’s Button schema says so (it maps to variant — do not promise hex on Button).**

#### 4.0.3 Size vocabulary

Not universal. `sm` / `lg` common; `md` often means “default, no class”. Pagination.size: `sm`/`lg` only. Modal.size: `sm`/`lg`/`xl`. Normalize `"md"` to default (no size class) where Bootstrap has no medium class.

#### 4.0.4 Grid

12 columns, mobile-first:

| Breakpoint | Min width |
|---|---|
| xs | 0 |
| sm | 576 px |
| md | 768 px |
| lg | 992 px |
| xl | 1200 px |
| xxl | 1400 px |

A tier applies at that width and above until overridden. Do not mutate caller dicts.

#### 4.0.5 Form value publishing (Input family)

Revision note (R1): integer `debounce` is a native extension; DBC/compat keep boolean semantics.

- `debounce=False`: publish every change. **DBC 2.0.4 contract (compat).**
- `debounce=True`: publish on Enter (`n_submit`) or blur (`n_blur`). **DBC 2.0.4 contract (compat).**
- `debounce: int` (milliseconds after typing stops, trailing): **native extension only.** On `dbc.Input` / `dbc.Textarea`, a non-bool `debounce` raises `UnsupportedPropError`. Manifest: `extension` on native, `supported` boolean on compat.
- Numeric `type="number"` / `range`: invalid or empty published as `None` on the Python side (DBC).
- Select: published value is **string** (`target.value`).
- IME composition: do not commit composition intermediates as values when debounce is not False — standard `compositionend` handling in the Vue control.

#### 4.0.6 Markup principles

- Semantic tags (`button`, `nav`, `ol`, `table`, `label`, `dialog`-equivalent structure).
- Structural Bootstrap classes always present (`container`, `row`, `col`, `btn`, `card`, …).
- Validation classes (`is-valid` / `is-invalid`) only when the corresponding props are set. This is not an application validation engine.
- No extra wrapper that DBC would not have if it would break CSS (`> .card-body` selectors, `.input-group > .form-control`). Selector-sensitive grouping components reject mixed text children (3.4.2).

#### 4.0.7 Rejected historical names

Instantiating these raises `TypeError` with a one-line migration hint:

`CardColumns`, `CardDeck`, `FormGroup`, `InputGroupAddon`, `Jumbotron`, `ListGroupItemHeading`, `ListGroupItemText`.

Do not export `Dropdown`, `PaginationItem`, `CarouselItem`, `CardTitle`, `CardText`.

Removed props (`Carousel.ride`, `Navbar.light`, …) are **absent from signatures**. Passing them is an unknown-kwarg `TypeError` (OQ11), not a present-but-forbidden parameter (that would pollute generated prop tables).

#### 4.0.8 Dash-specific dispositions (all components)

| DBC concept | Disposition |
|---|---|
| Callback graph / `Input`/`Output` | Excluded. Use NiceGUI handlers. |
| `persistence`, `persisted_props`, `persistence_type` | Adapted optional `persist=` (3.9). Default off. Requires public `id`. |
| Loading context / Spinner child delay based on Dash | Adapted: explicit `loading`. `display=auto` uses `loading`. |
| `loading_state` prop if present on generated classes | Unsupported; ignore with warning on native; `UnsupportedPropError` on compat. |
| Dash `Link` / internal routing on `NavLink`/`Button`/`Breadcrumb` | Adapted: `href` + `on_click`; internal navigation via NiceGUI `ui.navigate` when `external_link=False` and `href` is an in-app path. See Open question 6. |
| Pattern-matching ids | Excluded. |
| `_timestamp` props | Removed in DBC 2.0; reject. |
| `external_link` on Button | Only applied when the button renders as `<a>`. Never leaked onto `<button>` (DBC issue #1166 class of bug; issue verified 2026-09-20, state open). |

---

### 4.1 Layout family  
Docs slug: `layout` — Container, Row, Col, Stack

#### 4.1.1 Container — `bs.container` / `dbc.Container`

**Impl:** P, tag `div`.

**API sketch:**

```python
class Container(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        fluid: bool | str = False,
        id=None,
        class_name=None,
        className=None,
        style=None,
        tag: str = "div",
    ) -> None: ...
```

**Prop mapping:**

| Prop | Semantics |
|---|---|
| `fluid=False` | `class="container"` (responsive breakpoints). |
| `fluid=True` | `container-fluid`. |
| `fluid="sm"|"md"|"lg"|"xl"|"xxl"` | `container-{bp}` (Bootstrap 5). If DBC 2.0.4 only documents bool, still accept Bootstrap strings as a documented extension **only if** the extracted schema allows str; otherwise bool only. **Extract.** Proposed default if schema is bool-only: bool in compat; str allowed on native. |

**Markup:** `<div class="container ...">` (or `fluid` variant).

**JS:** none.

**Edge cases:** Nested containers are allowed (author’s problem). Do not add NiceGUI default padding classes.

#### 4.1.2 Row — `bs.row` / `dbc.Row`

**Impl:** P, tag `div`.

**API sketch:**

```python
class Row(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        align: str | None = None,          # start|center|end|stretch|baseline → align-items-*
        justify: str | None = None,        # start|center|end|around|between|evenly
        g: int | None = None,              # gutter 0–5 if in schema
        gx: int | None = None,
        gy: int | None = None,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Markup:** `<div class="row [align-items-*] [justify-content-*] [g-*]">`.

**Edge cases:** Gutters are Bootstrap utilities, not a second grid engine. Unknown align values: `ValueError` on native; compat may pass through class (proposed: validate both).

#### 4.1.3 Col — `bs.col` / `dbc.Col`

**Impl:** P, tag `div`.

**API sketch:**

```python
BreakpointValue = int | bool | str | dict  # dict keys: size, order, offset

class Col(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        width: BreakpointValue | None = None,  # base/xs
        xs=None, sm=None, md=None, lg=None, xl=None, xxl=None,
        align: str | None = None,              # start|center|end|stretch|baseline (self)
        class_name=None, style=None, id=None,
        order=None, offset=None,               # if present on DBC Col as shortcuts — extract
    ) -> None: ...
```

**Mapping rules (DBC Col):**

- Integer `1–12` → `col-{n}` or `col-{bp}-{n}`.
- `True` → `col` / `col-{bp}` (equal expand).
- `"auto"` → `col-auto` / `col-{bp}-auto`.
- `dict`: `size`, `order`, `offset` → `col-*`, `order-*`, `offset-*` (and bp variants).
- `width` is base/xs; **explicit `xs` takes precedence over `width`**.
- `width=0.5` is **not** half width; reject floats that are not documented.
- `align` → `align-self-*`.

**Markup example:**

```html
<div class="col-12 col-md-6 col-xl-4 offset-xl-2">...</div>
```

for `Col(..., xs=12, md=6, xl={"size": 4, "offset": 2})`.

**Validation:** Native surface validates size/order/offset ranges (1–12, order 0–5 or 1–12 per Bootstrap 5 — **extract Bootstrap 5.3 order utilities and match DBC**). Compat: same validation preferred (research allows a clearer library without pretending DBC’s schema was strict).

**JS:** none.

**Edge cases:** Do not copy/mutate the caller’s dict. `width=True` plus `md=6` is valid.

#### 4.1.4 Stack — `bs.stack` / `dbc.Stack`

**Impl:** P.

**API sketch:**

```python
class Stack(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        direction: str = "vertical",  # vertical|horizontal → vstack|hstack
        gap: int | None = None,       # 0–5
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Markup:** `<div class="vstack gap-2">` / `hstack`.

**Edge cases:** Not a flex engine with arbitrary breakpoints; keep DBC’s surface. Do not implement as `ui.column`.

---

### 4.2 Button family  
Docs slugs: `button`, `button_group`

#### 4.2.1 Button — `bs.button` / `dbc.Button`

**Impl:** P (native `<button>` or `<a>`). Click listener registered in `__init__`.

**API sketch:**

```python
class Button(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        color: str = "primary",
        outline: bool = False,
        size: str | None = None,          # sm|lg
        disabled: bool = False,
        active: bool = False,
        n_clicks: int = 0,                # compat observable; start value
        type: str = "button",             # button|reset|submit
        href: str | None = None,
        external_link: bool | None = None,
        download: str | bool | None = None,
        target: str | None = None,        # HTML target, not overlay target
        name: str | None = None,
        value: str | None = None,         # HTML value, extract if in schema
        on_click: Callable | None = None,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Color mapping:** `outline=False` → `btn btn-{color}`; `outline=True` → `btn btn-outline-{color}`. `color="link"` → `btn btn-link`. Unknown semantic colors: `ValueError` native; compat: still require the DBC enum if declared.

**Markup:**

- No `href`: `<button type="..." class="btn ..." :disabled>`.
- With `href`: `<a class="btn ..." href="..." role="button">` (Bootstrap pattern). `disabled` on links: `aria-disabled="true"`, `tabindex="-1"`, pointer-events none, **clicks do not increment `n_clicks`**.

**`external_link`:** If the control is an `<a>` and `external_link=True`, `target="_blank"` `rel="noopener noreferrer"` (confirm DBC behavior on extract). If not rendered as a link, **drop the prop** (do not put `external_link` on the DOM).

**Events:** click → `n_clicks += 1` then `on_click`. Disabled: no increment, no handler.

**Edge cases:** `type="submit"` inside `Form` participates in native submit. Do not use Quasar `ui.button`. `class_name` appended after `btn` classes. Mixed phrasing children allowed (3.4.2).

#### 4.2.2 ButtonGroup — `bs.button_group` / `dbc.ButtonGroup`

**Impl:** P.

```python
class ButtonGroup(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        size: str | None = None,
        vertical: bool = False,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Markup:** `<div class="btn-group [btn-group-sm|lg] [btn-group-vertical]" role="group">`.

**Edge cases:** Size is on the group, not rewritten onto children (Bootstrap sizes groups via group classes). Aria role `group` / `toolbar` only if DBC has a toolbar prop — extract. **Element children only** (selector-sensitive; 3.4.2).

---

### 4.3 Input family  
Docs slug: `input` — Input, Textarea, Select, Checkbox, Checklist, RadioButton, RadioItems, Switch  
Docs slug: `input_group` — InputGroup, InputGroupText  
(Form family is 4.4)

#### 4.3.1 Input — `bs.input` / `dbc.Input`

**Impl:** V, native `<input>`. `BootstrapValueElement`. Frontend: `model-value` + `update:modelValue`.

**Declared DBC type enum (2.0.4):** `text`, `number`, `password`, `email`, `range`, `search`, `tel`, `url`, `hidden`, `time`.  
**Known discrepancy:** DBC docs show `type="color"` but the 2.0.4 enum omits it. **Compat: enum without `color` (`UnsupportedPropError`).** Native: allow `color` as **extension**. Enforced because `bs.Input` and `dbc.Input` are distinct types (3.4.1).

**API sketch:**

```python
class Input(BootstrapValueElement):
    def __init__(
        self,
        value: str | float | None = "",
        *,
        type: str = "text",
        placeholder: str | None = None,
        size: str | None = None,             # sm|lg → form-control-sm/lg
        plaintext: bool = False,             # form-control-plaintext
        disabled: bool = False,
        readonly: bool = False,
        read_only: bool | None = None,       # native alias
        debounce: bool | int = False,        # int: native extension only
        n_submit: int = 0,
        n_blur: int = 0,
        valid: bool | None = None,           # True/False/None → is-valid/is-invalid/none
        invalid: bool | None = None,         # extract actual DBC valid/invalid props
        min=None, max=None, step=None,
        maxlength: int | None = None,
        autocomplete: str | None = None,
        name: str | None = None,
        list: str | None = None,
        pattern: str | None = None,
        required: bool = False,
        persist: str = "off",
        on_change=None, on_submit=None, on_blur=None,
        class_name=None, style=None, id=None,
        html_size: int | None = None,        # HTML size attr; not control size
    ) -> None: ...
```

Exact valid/invalid prop names: **extract** (`valid`/`invalid` vs `class_name` only). Proposed default: `valid: bool | None` and `invalid: bool | None`; if both True, `PropConflictError`.

**Markup:** `<input class="form-control [form-control-sm|lg] [is-valid|is-invalid] [form-control-plaintext]" />`. `type="range"` uses `form-range` (Bootstrap 5) if DBC does — **extract**.

**Debounce / counters:** Section 4.0.5. Enter on a single-line input increments `n_submit` and publishes value. Blur increments `n_blur` and publishes if debounce is True or numeric (flush pending). Compat: `debounce` must be `bool`.

**Numeric:** Python `value` is `int` if the string is integral and type is number, else `float`, else `None` if empty/invalid — **Open question 7**. Proposed default: match DBC source (`fast-isnumeric`): invalid → `None`; otherwise number type as JS number serialized to Python `int` when `value.is_integer()`, else `float`. Compat tests against DBC 2.0.4 behavior on a small harness (phase 1b).

**Edge cases:** Preserve caret on server-set value **if the value string is unchanged**. If Python sets a different value while focused, replace and move caret to end (document this). `hidden` type still participates in forms. Do not use `ui.input` (Quasar).

#### 4.3.2 Textarea — `bs.textarea` / `dbc.Textarea`

**Impl:** V, `<textarea class="form-control">`. `BootstrapValueElement`. Same frontend value contract.

Same debounce (bool on compat; int extension on native), valid/invalid, size, counters (`n_blur`; `n_submit` only if DBC documents it for textarea — extract; proposed: no `n_submit` unless in schema). `rows` prop. Do not intercept Enter unless debounce True requires “commit on blur only”.

#### 4.3.3 Select — `bs.select` / `dbc.Select`

**Impl:** V, native `<select class="form-select">`. **Not** Quasar select, **not** searchable, **not** multi (DBC boundary). Bootstrap native `multiple` is a possible **named extension** (`bs.select_multiple`) — **not** in v1 inventory.

Revision note (R1): `invalid` added to match Input and DBC.

```python
class Select(BootstrapValueElement):
    def __init__(
        self,
        value: str | None = None,
        *,
        options: list | None = None,     # extract DBC option shape
        placeholder: str | None = None,
        size: str | None = None,         # sm|lg
        html_size: int | None = None,    # HTML size (rows visible)
        disabled: bool = False,
        required: bool = False,
        valid: bool | None = None,
        invalid: bool | None = None,     # is-invalid; PropConflictError if both True
        on_change=None,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Value contract:** always a **string** on the Python side after user interaction, even if an option was numeric in Python. Initial `value=1` vs option `"1"`: normalize with `str` for comparison when publishing; document that authors should use strings for stable identity.

**Options:** Extract DBC’s `options` list-of-dicts (`label`, `value`, `disabled`). If DBC Select uses children `<option>` instead, support children as well. **Proposed default if both exist in schema:** `options` prop primary, children allowed as `<option>` elements.

**Placeholder:** disabled hidden first option when value is None/empty, if DBC does this.

**Markup:** `<select class="form-select [form-select-sm|lg] [is-valid|is-invalid]">`.

#### 4.3.4 Checkbox — `bs.checkbox` / `dbc.Checkbox`

**Impl:** V. `BootstrapValueElement`. Boolean `value`. Label association (`id` + `for` or wrapping label — follow DBC markup). Classes `form-check`, `form-check-input`, `form-check-label`. `input_checked_style` if in schema.

Standalone; not a group. `on_change(bool)`.

#### 4.3.5 Switch — `bs.switch` / `dbc.Switch`

Same storage as Checkbox; add `form-switch` on the `form-check` wrapper. Do not use a second value model.

#### 4.3.6 RadioButton — `bs.radio_button` / `dbc.RadioButton`

Standalone radio primitive. `name` groups in HTML. `value` is the boolean “this radio is selected” **or** the group value depending on DBC schema — **extract**. Research: “standalone radio control.” Proposed: boolean checked state plus `value` HTML attribute for grouping, matching native radio.

Do not remove this component because RadioItems exists.

#### 4.3.7 Checklist — `bs.checklist` / `dbc.Checklist`

**Impl:** H. `value: list` of selected option values. `options` list. `inline` → `form-check-inline`. Disabled options. Stable identities: do not reuse DOM nodes across option value changes without keying by option value.

**Edge cases:** Replacing `options` drops unknown selected values (document). Inline vs stacked. Switch-style checklist if DBC has `switch` prop — extract.

#### 4.3.8 RadioItems — `bs.radio_items` / `dbc.RadioItems`

Like Checklist but `value` is a **scalar**. Same options/inline/disabled. Keyboard: native radio group (one tab stop).

#### 4.3.9 InputGroup — `bs.input_group` / `dbc.InputGroup`

**Impl:** P. `<div class="input-group [input-group-sm|lg]">`. Children are inputs, `InputGroupText`, buttons. **Do not wrap children in extra divs** that break `> .form-control` CSS. **Element children only** (3.4.2).

Size on the group only.

#### 4.3.10 InputGroupText — `bs.input_group_text` / `dbc.InputGroupText`

**Impl:** P. `<span class="input-group-text">`.

---

### 4.4 Form family  
Docs slug: `form` — Form, FormFloating, Label, FormText, FormFeedback

#### 4.4.1 Form — `bs.form` / `dbc.Form`

**Impl:** P, tag `form`.

```python
class Form(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        action: str | None = None,
        method: str | None = None,
        novalidate: bool = False,
        on_submit: Callable | None = None,
        prevent_default: bool = True,     # native; see below
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Submit policy (library contract, because DBC/Dash apps rarely do full page posts):**

- Native default: `prevent_default=True` — listen `submit`, `event.preventDefault()`, call `on_submit`.
- If `action` is set and `prevent_default=False`, allow native navigation.
- Compat: extract DBC Form props; if no submit handler exists in DBC, still provide native `on_submit` as extension.

**Markup:** `<form class="...">`. Optional `row`/`g-*` if DBC has `floating`/`validated` — extract `validated` → `was-validated`.

#### 4.4.2 Label — `bs.label` / `dbc.Label`

**Impl:** P, `<label class="form-label" for="...">`. `html_for` / `for_` mapping: DBC may use `html_for` or `_for` or `for` — **extract**. Proposed native: `html_for: str | None`. Width/column sizing if DBC Label is also used as grid label (`col-form-label`) — extract.

Not NiceGUI `ui.label` (which is a div/span in practice). Use a real `<label>`.

#### 4.4.3 FormText — `bs.form_text` / `dbc.FormText`

P, `<div class="form-text">` or `<small>` per DBC/Bootstrap. Extract tag.

#### 4.4.4 FormFeedback — `bs.form_feedback` / `dbc.FormFeedback`

P. `type="valid"|"invalid"` → `valid-feedback` / `invalid-feedback`. Tooltip variants if in schema (`invalid-tooltip`). Must be sibling of the control per Bootstrap; we do not auto-move it.

#### 4.4.5 FormFloating — `bs.form_floating` / `dbc.FormFloating`

P, `<div class="form-floating">`. **Child order is part of the contract:** Bootstrap requires control then label. Document; do not silently reorder unless DBC does. Native helper: `FormFloating(control, label)` that orders correctly if both passed as args — extension.

---

### 4.5 Card family  
Docs slug: `card`

All **P**. Do **not** auto-insert `CardBody` if the user puts text in `Card` (DBC does not silently wrap). Docs can show the recipe.

| Class | Tag / classes | Notes |
|---|---|---|
| Card | `div.card` | `color` → `text-bg-*` or `bg-*` + `text-*` per Bootstrap 5.3 + DBC (extract). |
| CardBody | `div.card-body` | Padding lives here, not on Card. |
| CardHeader | `div.card-header` | |
| CardFooter | `div.card-footer` | |
| CardGroup | `div.card-group` | Selector-sensitive grouping: element children only. |
| CardImg | `img.card-img` / `card-img-top` / `card-img-bottom` | `src`, `alt` required for a11y when informational; decorative `alt=""`. `top`/`bottom`/`overlay` position prop as in DBC. |
| CardImgOverlay | `div.card-img-overlay` | |
| CardLink | `a.card-link` | `href`, external_link rules as Button. |

No `CardTitle` / `CardText` exports. Docs show `class_name="card-title"` on a heading: `ui.element("h5").classes("card-title")` inside the Card (Mode B: Card lives under `bs.scope`, so utilities apply). **v1 does not ship `bs.element`.**

**Card color:** extract whether DBC uses `color` + `outline` like older Bootstrap cards or `color` as `text-bg-{color}`.

---

### 4.6 List group family  
Docs slug: `list_group`

Revision note (R1): `ListGroup` tag is fixed at `__init__`; no post-hoc remount when children appear.

**ListGroup** — P. Tag is decided in `__init__` and never changed (NiceGUI tags are fixed at construction; context-manager children do not exist yet).

| Condition at `__init__` | Tag |
|---|---|
| explicit `tag=` | that tag |
| `numbered=True` (and no `tag`) | `ol` |
| otherwise | **`div`** |

Default `div` is valid for both static and actionable items under the preferred context-manager path (`div > a|button|div.list-group-item`). Do **not** “switch to `div` when any child is not an `li`” after the fact.

`flush` → `list-group-flush`. `numbered` → `list-group-numbered` (with `ol`). `horizontal` → `list-group-horizontal` / `list-group-horizontal-{bp}`. Extract DBC’s `tag` prop and keep it as the override.

Contextvar (native `with list_group():` only): while entered, `ListGroupItem` default tag is `li` if the group tag is `ul`/`ol`, else `div`. Nested `children=` expressions construct items **before** the group, so they cannot read the contextvar; they use the item rules below. Authors using `numbered=True` with `children=` must pass `tag="li"` on items (documented). Invalid combinations (`ol > a`) are author errors; we do not remount.

**ListGroupItem** — P. Classes `list-group-item`, `active`, `disabled`, `list-group-item-action`, `list-group-item-{color}`. Tag at **item** `__init__`:

- explicit `tag=` wins;
- else `href` → `a`;
- else `action` → `button`;
- else contextvar default if inside `with ListGroup`;
- else `div`.

Disabled links: same as Button. Click handler + `n_clicks` if DBC has it — extract.

Selector-sensitive: `ListGroup` allows element children only.

No `ListGroupItemHeading` / `ListGroupItemText`.

---

### 4.7 Table — `bs.table` / `dbc.Table`  
Docs slug: `table`

**Impl:** P, semantic `<table class="table">`.

Boolean/enum props (extract exact set; Bootstrap 5 table utilities): `bordered`, `borderless`, `striped`, `hover`, `small`/`size`, `responsive` (bool or breakpoint → wrap in `div.table-responsive[-bp]`), `color`, `striped_columns`. **`dark` was removed in DBC 2.0** — reject. Color mode comes from theme.

Children: caption, thead/tbody via nested elements or raw rows. Native: allow constructing with `ui.element("thead")` children.

**`Table.from_dataframe`** — handwritten classmethod, pandas **optional extra**.

Revision note (R1): `index` default is `True` to match DBC `_table.py`.

```python
@classmethod
def from_dataframe(
    cls,
    df: object,
    *,
    columns=None,
    header: bool = True,
    index: bool = True,                  # match DBC _table.py
    index_label: str | None = None,
    date_format: str | None = None,
    float_format: str | Callable | None = None,
    # plus DBC’s remaining kwargs — extract from dash_bootstrap_components/_table.py
    **table_props,
) -> Table: ...
```

Behavior to match DBC `_table.py`: column subset, headers, indexes, number/date formatting, **multilevel column headers**. Builds ordinary `th`/`td` Python elements, not a grid widget. If pandas is missing: `ImportError` with extra name `pandas`.

**Edge cases:** Empty frame → header-only table if `header=True`. Do not coerce dtypes silently beyond DBC. Multilevel columns → multiple `<tr>` in `<thead>`.

---

### 4.8 Badge — `bs.badge` / `dbc.Badge`  
Docs slug: `badge`

P. `span.badge` or `a.badge` if `href`. `color` → `text-bg-{color}` (Bootstrap 5.3) unless DBC still uses `bg-*`. `pill` → `rounded-pill`. `text_color` if in schema. Do not communicate status by color alone — docs a11y note (include text).

---

### 4.9 Progress — `bs.progress` / `dbc.Progress`  
Docs slug: `progress`

P. Outer `div.progress` + inner `div.progress-bar`.

Props (extract; typical DBC): `value`, `min`, `max`, `label`, `animated`, `striped`, `color`, `height`, `bar_class_name` / `bar_style`. Multiple bars: children that are also Progress bars **or** stacked via children. If DBC Progress is only a single bar with optional children as nested bars, follow that.

ARIA: `role="progressbar"`, `aria-valuenow/min/max`. Determinate only unless DBC has indeterminate — extract.

No JS animation callbacks; CSS handles stripes/animation.

---

### 4.10 Placeholder — `bs.placeholder` / `dbc.Placeholder`  
Docs slug: `placeholder`

P. `placeholder` / `placeholder-glow` / `placeholder-wave`, size `placeholder-xs|sm|lg`, width utilities or `xs=6`-style grid widths if DBC reuses col sizes — extract. DBC 2.0 added loading-target and display controls like Spinner — **adapt** with explicit `loading` / `display`; do not read Dash loading.

Decorative: `aria-hidden="true"` when empty skeleton. If wrapping content, `aria-busy` when loading.

---

### 4.11 Alert — `bs.alert` / `dbc.Alert`  
Docs slug: `alert`

**Impl:** P if `dismissable=False` (DBC spelling — **extract**; often `dismissable` with an `a`). V if dismissible (fade + close button).

```python
class Alert(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        color: str = "primary",
        dismissable: bool = False,     # spelling from DBC
        fade: bool = True,
        is_open: bool = True,
        duration: int | None = None,   # extract
        on_dismiss=None,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Markup:** `<div class="alert alert-{color} [alert-dismissible] [fade show]" role="alert">` + optional close `button.btn-close`.

**Behavior:** Close sets `is_open=False`, emits `dismiss`. Duration timer if in schema. If `is_open` False, do not display (or fade out). Sync Python state when the user clicks close (do not leave `is_open=True`).

**Edge cases:** `color="danger"` still `role="alert"` (interruptive). Consider `role="status"` for non-danger native extension — do not change DBC default.

---

### 4.12 Spinner — `bs.spinner` / `dbc.Spinner`  
Docs slug: `spinner`

**Impl:** P (+ overlay root if fullscreen).

```python
class Spinner(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        color: str | None = None,       # semantic or arbitrary CSS color
        type: str = "border",           # border|grow
        size: str | None = None,        # sm
        loading: bool | None = None,    # analogue
        display: str = "auto",          # auto|show|hide
        delay_show: int | None = None,  # extract names
        delay_hide: int | None = None,
        fullscreen: bool = False,
        spinner_style: dict | None = None,
        spinner_class_name: str | None = None,
        spinnerClassName: str | None = None,  # deprecated alias
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Markup:** `<div class="spinner-border [text-{color}]" role="status">` or `spinner-grow`. Children: when used as wrapper, children sit beside/under; spinner visibility from `display`/`loading`. Fullscreen: fixed overlay in overlay root.

**Styling surface:** DBC Spinner does **not** use generic style the same way — `spinner_style` targets the spinner node; `class_name` targeting extract (outer vs spinner). Follow DBC 2.0.4 source.

**No** `window.dash_component_api`.

**Edge cases:** Arbitrary hex `color` → inline `style="color: ..."` on the spinner. `display="hide"` never shows even if `loading`. Show/hide delays: timers cleared on unmount.

---

### 4.13 Navigation family  
Docs slugs: `nav`, `navbar`, `breadcrumb`, `dropdown_menu`, `tabs`, `pagination`

#### 4.13.1 Nav — `bs.nav` / `dbc.Nav`

P. `<ul class="nav [nav-tabs|nav-pills] [flex-column] [nav-fill|nav-justified]">` or `nav` tag — extract `pills`, `tabs`, `fill`, `justified`, `vertical`, `navbar` (becomes `navbar-nav`).

#### 4.13.2 NavItem — `bs.nav_item` / `dbc.NavItem`

P. `<li class="nav-item">`.

#### 4.13.3 NavLink — `bs.nav_link` / `dbc.NavLink`

P. `<a class="nav-link [active] [disabled]">` or `<button>` if no href. Props: `active`, `disabled`, `href`, `external_link`, `n_clicks`. Active is **author-controlled** (DBC does not magically route). For NiceGUI multi-page, gallery examples set `active` from the current path.

Internal vs external: Open question 6. Proposed: `href` starting with `http(s):` or `external_link=True` → real navigation; otherwise `on_click` + `ui.navigate.to(href)` if href set and client-side.

Phrasing mixed children allowed (e.g. `["Messages ", Badge("4")]`).

#### 4.13.4 Navbar — `bs.navbar` / `dbc.Navbar`

Revision note (R1): `fixed` and `sticky` are in the v1 contract (not deferred).

P/H. `<nav class="navbar [navbar-expand-{bp}]">`. `color` / `dark` as `data-bs-theme` or `navbar-dark`/`bg-*` — Bootstrap 5.3 prefers `data-bs-theme="dark"` on navbar plus `bg-*`. **`light` was removed in DBC 2.0.** Extract remaining color props.

```python
class Navbar(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        color: str | None = None,
        dark: bool | None = None,
        expand: bool | str | None = None,   # True|False|sm|md|lg|xl|xxl
        fixed: str | None = None,           # "top" | "bottom" → fixed-top / fixed-bottom
        sticky: str | None = None,          # "top" → sticky-top
        class_name=None, style=None, id=None,
    ) -> None: ...
```

`fixed` and `sticky` together → `PropConflictError`. Values other than the documented enums → `ValueError` (both surfaces).

Contains `NavbarBrand`, `NavbarToggler`, `Collapse`/`Offcanvas` for collapsing content. Toggler `id`/`target` wiring: native: pass the collapse element ref; compat: public id string.

#### 4.13.5 NavbarBrand — `bs.navbar_brand` / `dbc.NavbarBrand`

P. `<a class="navbar-brand">` or `span` if no href.

#### 4.13.6 NavbarToggler — `bs.navbar_toggler` / `dbc.NavbarToggler`

H. `<button class="navbar-toggler">` with `navbar-toggler-icon`. Controls a Collapse via Vue/controller, **not** `data-bs-toggle` auto plugin (avoids double ownership). `on_click` toggles the linked collapse’s `is_open`.

#### 4.13.7 NavbarSimple — `bs.navbar_simple` / `dbc.NavbarSimple`

**Composition convenience**, not a second implementation. Builds Navbar + Brand + Toggler + Collapse + Nav from:

Typical DBC props (extract exact): `brand`, `brand_href`, `children` (nav items), `color`, `dark` (if still present), `expand`, `fluid`, `fixed`, `sticky`, `links` vs children. **`light` removed.** `fixed`/`sticky` pass through to the inner `Navbar`.

Implementation: function/class that constructs primitives in `__init__` with context. Must remain customizable via children.

#### 4.13.8 Breadcrumb — `bs.breadcrumb` / `dbc.Breadcrumb`

P. `<nav aria-label="breadcrumb"><ol class="breadcrumb">`. Items from `items: list[dict]` (`label`, `href`, `active`) and/or children. Current item: `aria-current="page"`, no link. Extract DBC item schema.

#### 4.13.9 DropdownMenu — `bs.dropdown_menu` / `dbc.DropdownMenu`

**Impl:** V. **Internal open state on compat.** Removed: `addon_type`, `right`.

```python
class DropdownMenu(BootstrapElement):
    def __init__(
        self,
        children=None,                     # DropdownMenuItem(s)
        *,
        label: str | None = None,
        color: str = "secondary",
        size: str | None = None,
        direction: str = "down",           # down|start|up|end
        menu_variant: str | None = None,   # light|dark
        align_end: bool | None = None,     # extract (replaces right)
        disabled: bool = False,
        nav: bool = False,                 # nav-item + nav-link toggle
        caret: bool = True,
        in_navbar: bool = False,
        group: bool = False,               # split / btn-group
        toggle_style: dict | None = None,
        toggle_class_name: str | None = None,
        on_item_click=None,                # native
        is_open: bool | None = None,       # native extension; compat: UnsupportedPropError
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Markup:** `div.dropdown` / `btn-group` + toggle `button.dropdown-toggle` + `ul.dropdown-menu`. Color on toggle as Button. Arbitrary CSS color if DBC DropdownMenu supports it (research: some components do — extract; if only semantic, validate).

**JS:** Section 3.7.3. Keyboard per Bootstrap 5 dropdown (Arrow up/down, Home/End, Esc, Tab).

#### 4.13.10 DropdownMenuItem — `bs.dropdown_menu_item` / `dbc.DropdownMenuItem`

P/V child. Variants: default item, `header=True` → `h6.dropdown-header`, `divider=True` → `hr.dropdown-divider`. `disabled`, `active`, `href`, `n_clicks`, `toggle` (whether clicking closes menu — extract default True).

#### 4.13.11 Tabs — `bs.tabs` / `dbc.Tabs` and Tab — `bs.tab` / `dbc.Tab`

**Impl:** H/V. **Tabs consumes Tab children**, not a `value` list of labels only.

Revision note (R1): `card` is in the v1 contract.

```python
class Tabs(BootstrapElement):
    def __init__(
        self,
        children=None,                     # Tab instances
        *,
        active_tab: str | None = None,
        card: bool = False,                # card-header-tabs / card body panes
        persist: str = "off",
        on_change=None,                    # native; tab id
        class_name=None, style=None, id=None,
    ) -> None: ...

class Tab(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        label: str | None = None,
        tab_id: str | None = None,         # extract DBC name (tab_id vs id)
        disabled: bool = False,
        class_name=None,                   # pane
        label_class_name=None,
        label_style=None,
        style=None, id=None,
    ) -> None: ...
```

**Behavior:**

- If `active_tab` missing, **first enabled tab**.
- Missing tab ids receive generated `tab-0`, `tab-1`, … (DBC: `tab-i`). Generation must be **stable for the child order at construct**; if children are replaced, recompute without colliding; do not reshuffle ids of remaining tabs if public ids exist.
- `active_tab` is writable; clicking a tab updates it and emits `change`.
- Persist analogue on `active_tab`.
- `card=True`: tab list uses `card-header card-header-tabs`; panes sit in `card-body` (Bootstrap card-tabs recipe). Extract exact DBC class names.
- Keyboard: left/right (or up/down if vertical — extract), Home/End. `role="tablist"` / `tab` / `tabpanel`, `aria-selected`, `aria-controls`.
- Lazy rendering: **extension** `lazy=False` by default (DBC keeps panes in DOM). If `lazy=True`, inactive panes not built — document as extension.

**Dynamic children:** DBC 2.0.2/2.0.3 fixed Tabs update bugs. Tests: insert/remove/replace tabs, remount, nested tabs.

**Do not** use NiceGUI `ui.tabs` (Quasar).

#### 4.13.12 Pagination — `bs.pagination` / `dbc.Pagination`

**Impl:** P/H. **Generates its own page items** (no `PaginationItem` export). Docs comments that mention PaginationItem are DBC source bugs; we do not export one.

```python
class Pagination(BootstrapElement):
    def __init__(
        self,
        *,
        max_value: int,                    # required
        min_value: int = 1,
        step: int = 1,
        active_page: int = 1,
        size: str | None = None,           # sm|lg
        fully_expanded: bool | None = None,
        first_last: bool | None = None,
        previous_next: bool | None = None,
        on_change=None,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

Extract remaining DBC props (`n_links`, icons, etc.).

**Behavior:** `active_page` defaults to 1. Out-of-range set clamps or ignores — **extract**; proposed: clamp to `[min_value, max_value]` on user click; Python set raises or clamps (proposed: clamp + warning). Disabled previous/next at ends. Clicks update `active_page` (not navigation hrefs unless `href` template exists in schema).

**Markup:** `<nav><ul class="pagination [pagination-sm|lg]">` with `page-item` / `page-link`.

**A11y:** `aria-current="page"` on active; `aria-label` on nav.

---

### 4.14 Overlay and disclosure family  
Docs slugs: `accordion`, `collapse`, `fade`, `modal`, `offcanvas`

#### 4.14.1 Accordion — `bs.accordion` / `dbc.Accordion`  
AccordionItem — `bs.accordion_item` / `dbc.AccordionItem`

**Impl:** V.

```python
class Accordion(BootstrapElement):
    def __init__(
        self,
        children=None,                     # AccordionItem
        *,
        active_item: str | list[str] | None = None,
        always_open: bool = False,
        start_collapsed: bool = False,
        flush: bool = False,
        persist: str = "off",
        on_change=None,
        class_name=None, style=None, id=None,
    ) -> None: ...

class AccordionItem(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        title: str | None = None,
        item_id: str | None = None,        # extract name
        class_name=None, title_class_name=None,
        style=None, id=None,
    ) -> None: ...
```

**State shape:** `always_open=False` → `active_item` is a single id or None. `always_open=True` → list of ids. **Do not** silently keep a scalar when `always_open` is True.

**Defaults:** first item selected unless `start_collapsed`. Persistence analogue on `active_item`.

**Markup:** `div.accordion` > `div.accordion-item` > `h2.accordion-header` + `button.accordion-button` + `div.accordion-collapse` + `div.accordion-body`. Header buttons `aria-expanded`.

**JS:** Vue height transition; coordinated close in single-open mode.

**Edge cases:** Unknown `active_item` id: ignore extra, don’t crash. Changing `always_open` at runtime converts scalar↔list.

#### 4.14.2 Collapse — `bs.collapse` / `dbc.Collapse`

**Impl:** V.

```python
class Collapse(OverlayElement):  # disclosure, not overlay root
    def __init__(
        self,
        children=None,
        *,
        is_open: bool = False,
        navbar: bool = False,              # navbar-collapse class
        dimension: str = "height",         # extract width support
        on_show=None, on_shown=None, on_hide=None, on_hidden=None,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Markup:** `div.collapse [show] [navbar-collapse]`. Tailwind fight: Section 3.8.3.

**JS:** desired/actual; reduced motion; delete during animation.

Navbar collapsible: horizontal wrap at breakpoint is CSS (`navbar-expand-*`); JS only toggles `show` below the breakpoint. Do not run height animation incorrectly on expanded navbars (Bootstrap’s navbar collapse is special). Test at `expand="lg"` across the lg breakpoint.

#### 4.14.3 Fade — `bs.fade` / `dbc.Fade`

**Impl:** V. **`is_in`, not `is_open`.** (DBC docs have historically said `is_open` in a comment — that is a DBC bug. We implement `is_in`.)

Extract: timeout, appear, enter, exit, unmount_on_exit. Native convenience `.show()`/`.hide()` map to `is_in`.

#### 4.14.4 Modal family

**Modal**, **ModalHeader**, **ModalTitle**, **ModalBody**, **ModalFooter** — H/V composite.

```python
class Modal(OverlayElement):
    def __init__(
        self,
        children=None,
        *,
        is_open: bool = False,
        size: str | None = None,           # sm|lg|xl
        fullscreen: bool | str = False,    # True or sm-down|md-down|...|xxl-down
        backdrop: bool | str = True,       # True|False|"static"
        centered: bool = False,
        scrollable: bool = False,
        fade: bool = True,
        keyboard: bool = True,             # extract
        enforceFocus: bool | None = None,  # compat name
        enforce_focus: bool | None = None, # native
        labelledby: str | None = None,
        dialog_class_name: str | None = None,
        dialog_style: dict | None = None,
        content_class_name: str | None = None,
        content_style: dict | None = None,
        backdrop_class_name: str | None = None,
        backdrop_style: dict | None = None,
        class_name: str | None = None,     # OUTER modal (DBC 2.0 breaking change)
        dialogStyle=None, contentStyle=None,  # deprecated aliases
        on_show=None, on_shown=None, on_hide=None, on_hidden=None, on_dismiss=None,
        style=None, id=None,
    ) -> None: ...
```

**DBC 2.0 styling targets:** `class_name` → outer modal; dialog styling → `dialog_class_name` / `dialog_style`. Do not “fix” this back to v1.

**Markup (Bootstrap 5.3):**

```html
<div class="modal [fade] [show]" tabindex="-1" role="dialog" aria-modal="true">
  <div class="modal-dialog [modal-sm|lg|xl] [modal-dialog-centered] [modal-dialog-scrollable] [modal-fullscreen*]">
    <div class="modal-content">
      <!-- header / body / footer children -->
    </div>
  </div>
</div>
```

Backdrop is a sibling in the overlay root: `div.modal-backdrop [fade] [show]`.

**ModalHeader:** `div.modal-header`; optional close button (`btn-close`) that dismisses parent Modal. Extract `close_button` prop.

**ModalTitle:** `h5.modal-title` (or `h1`–`h6` via tag prop). Must have an id for `aria-labelledby`.

**ModalBody / ModalFooter:** `div.modal-body` / `div.modal-footer`.

**Behavior:** Section 3.7.3. Dismissal sets `is_open=False`. One modal at a time (Bootstrap). Opening a second: **proposed default:** close the first, then open the second (sequential), documented. Nested modal markup is not supported.

**Focus:** on `shown`, focus first tabbable or the dialog. `enforceFocus` true: if focus leaves, pull back.

**Children updates while open** must not reset scroll or destroy focus unless the focused node was replaced.

#### 4.14.5 Offcanvas — `bs.offcanvas` / `dbc.Offcanvas`

**Impl:** V. Props (extract): `is_open`, `placement` (`start|end|top|bottom`), `backdrop` bool|"static", `scroll`, `keyboard`, `title`, auto header/body or children, `on_*` transition events.

Markup: `div.offcanvas offcanvas-{placement}`. Shared overlay service. z-index: backdrop 1040, panel 1045 (3.8.2). Responsive offcanvas (`offcanvas-lg`) if in schema.

---

### 4.15 Popover and Tooltip  
Docs slugs: `popover`, `tooltip`

#### 4.15.1 Tooltip — `bs.tooltip` / `dbc.Tooltip`

**Impl:** V (proposed) with Floating UI. Target required.

```python
class Tooltip(BootstrapElement):
    def __init__(
        self,
        children=None,                     # tooltip text
        *,
        target: str | BootstrapElement,
        placement: str = "auto",           # extract enum
        trigger: str | None = None,        # hover focus click
        delay: dict | int | None = None,
        is_open: bool | None = None,       # if DBC exposes it — extract
        autohide: bool | None = None,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

If DBC Tooltip is a wrapper around children rather than `target=`, extract and follow **DBC’s constructor**, not React-Bootstrap’s. Research says “anchored to a target.”

**Markup:** `div.tooltip.bs-tooltip-*` with `tooltip-inner` and arrow. Role `tooltip`.

**Cleanup:** hide on target unmount; dispose listeners.

#### 4.15.2 Popover — `bs.popover` / `dbc.Popover`  
PopoverHeader, PopoverBody

**Impl:** V, rich children.

Removed: `innerClassName` / `inner_class_name`.

Body/header are real components in the default slot, not HTML strings. Target + placement + trigger like Tooltip. `is_open` if in DBC schema (often yes for popover).

**A11y:** `role="tooltip"` vs `dialog` — follow Bootstrap 5.3 (popover is typically `role="tooltip"` even when richer; interactive content is a known limitation). Document.

---

### 4.16 Toast — `bs.toast` / `dbc.Toast`  
Docs slug: `toast`

**Impl:** V.

DBC defaults to **open**, **not dismissible**, **no autohide timer unless `duration` is set**. Do not copy `ui.notify` defaults (short, autohide).

Revision note (R1): DBC Toast has no `color` prop; it is not in the v1 contract.

```python
class Toast(BootstrapElement):
    def __init__(
        self,
        children=None,
        *,
        is_open: bool = True,
        header: str | None = None,
        icon: str | None = None,
        dismissable: bool = False,
        duration: int | None = None,       # ms; None = no timer
        delay: int | None = None,          # extract alias of duration
        on_dismiss=None,
        class_name=None, header_class_name=None, body_class_name=None,
        style=None, id=None,
    ) -> None: ...
```

**Markup:** `div.toast [show]` with `toast-header` / `toast-body`. Container positioning via parent `toast-container` — provide native `bs.toast_container` **only if** DBC exports it (it does **not** in the 66). Authors wrap with `ui.element("div").classes("toast-container position-fixed ...")` inside `bs.scope`. Docs recipe.

**JS:** show/hide classes; timer; dismiss button; live region.

---

### 4.17 Carousel — `bs.carousel` / `dbc.Carousel`  
Docs slug: `carousel`

**Impl:** V. **`items` is a list of dicts**, not `CarouselItem` children. `ride` is not a parameter; passing it is an unknown-kwarg `TypeError` (4.0.7).

Revision note (R1): `slide` added; `ride` omitted from the signature.

```python
class Carousel(BootstrapElement):
    def __init__(
        self,
        *,
        items: list[dict],
        active_index: int = 0,
        controls: bool = True,
        indicators: bool = True,
        interval: int | bool | None = 5000,  # extract default
        slide: bool = True,                  # class "slide" for CSS transition
        variant: str | None = None,          # dark — extract
        persist: str = "off",
        on_change=None,
        class_name=None, style=None, id=None,
    ) -> None: ...
```

**Item dict keys:** extract (`src`, `alt`, `caption`, `header`, `img_class_name`, …). Unknown keys ignored.

**Behavior:** zero-based index; wrap around; pause on hover if schema says; controls/indicators; interval `False` disables autoplay. `slide=False` omits the `slide` class (no CSS slide animation). Persist analogue on `active_index`.

**Markup:** `div.carousel [slide]` + inner + items + indicators + prev/next.

**Edge cases:** empty `items`; `active_index` out of range → clamp 0; items length shrinks → clamp; do not export CarouselItem.

---

### 4.18 Miscellaneous content

Covered above: Badge, Card*, ListGroup*, Table, Progress, Placeholder, Carousel.

---

### 4.19 Theme and icon modules (not components)

Not part of the 66. Still ship:

**`nicegui_bootstrap_components.themes`** — URL or bundled asset keys:

`BOOTSTRAP`, `GRID`, and:

`CERULEAN`, `COSMO`, `CYBORG`, `DARKLY`, `FLATLY`, `JOURNAL`, `LITERA`, `LUMEN`, `LUX`, `MATERIA`, `MINTY`, `MORPH`, `PULSE`, `QUARTZ`, `SANDSTONE`, `SIMPLEX`, `SKETCHY`, `SLATE`, `SOLAR`, `SPACELAB`, `SUPERHERO`, `UNITED`, `VAPOR`, `YETI`, `ZEPHYR`.

DBC 2.0.4 points these at Bootstrap/Bootswatch **5.3.6 CDN URLs**. This library **bundles** equivalent CSS (Section 5, 9) and still exposes the same **constant names**. Values: native use is package resource paths / setup keys, not Dash `external_stylesheets`. Compat module `dbc.themes` may expose the same CDN URLs as DBC for authors who want DBC-identical URL strings, plus bundled names. **Proposed default:** `themes.BOOTSTRAP` is an object with `.cdn` (pinned URL) and `.bundled` (package resource). `setup(theme=themes.FLATLY)` uses bundled.

**`nicegui_bootstrap_components.icons`:** stylesheet constants for Bootstrap Icons **1.11.3** and Font Awesome **6.7.2**. No `Icon` component. `setup(icons="bootstrap"|"fontawesome"|None)`.

---

### 4.20 Jumbotron (docs-only)

No export. Docs page `jumbotron` recreates the old appearance with `bs.container`, utility classes (`p-5`, `rounded-3`, `bg-body-tertiary`, etc.) matching DBC’s composition recipe. Copy the pedagogical structure, not pixel-identical DBC docs prose.

---

### 4.21 Native helpers that are **not** DBC exports

Allowed only if clearly namespaced and documented as extensions:

| Helper | Purpose |
|---|---|
| `bs.setup` / `setup` | Assets + mode (process-level). |
| `ThemeController` | Per-client color mode and theme swap. |
| `bs.scope` | Mode B island / Reboot scope-anchor (`div.ngbs`). Not required in Mode A. |
| `Modal.open/.close` | Native methods setting `is_open`. |
| `DropdownMenu.is_open` | Native extension (`bs` only). |
| `prevent_close` on Modal | Native extension. |
| `Table.from_dataframe` | DBC has this; ship it. |

Do **not** ship `bs.element` in v1. Users use `ui.element("h5").classes("card-title")` inside `bs.scope` / Card. Do not add `bs.jumbotron`, `bs.dropdown`, `bs.card_title`.

---

### 4.22 Complete export checklist (66)

Implementation CI asserts `__all__` equals:

`Accordion`, `AccordionItem`, `Alert`, `Badge`, `Breadcrumb`, `Button`, `ButtonGroup`, `Card`, `CardBody`, `CardFooter`, `CardGroup`, `CardHeader`, `CardImg`, `CardImgOverlay`, `CardLink`, `Carousel`, `Checkbox`, `Checklist`, `Col`, `Collapse`, `Container`, `DropdownMenu`, `DropdownMenuItem`, `Fade`, `Form`, `FormFeedback`, `FormFloating`, `FormText`, `Input`, `InputGroup`, `InputGroupText`, `Label`, `ListGroup`, `ListGroupItem`, `Modal`, `ModalBody`, `ModalFooter`, `ModalHeader`, `ModalTitle`, `Nav`, `Navbar`, `NavbarBrand`, `NavbarSimple`, `NavbarToggler`, `NavItem`, `NavLink`, `Offcanvas`, `Pagination`, `Placeholder`, `Popover`, `PopoverBody`, `PopoverHeader`, `Progress`, `RadioButton`, `RadioItems`, `Row`, `Select`, `Spinner`, `Stack`, `Switch`, `Tab`, `Table`, `Tabs`, `Textarea`, `Toast`, `Tooltip`.

Plus modules: `themes`, `icons`. Plus `Table.from_dataframe`. Plus native-only `bs.scope` (not in the 66, not re-exported on `dbc`).

CI also asserts `bs.Button is not dbc.Button` and that each pair shares `component_name`.

---

## 5. Theming

### 5.1 Principles

- DBC ships **no** Bootstrap CSS (`_css_dist` empty). Users supplied CDN URLs. This library **does** ship pinned CSS because NiceGUI apps should work offline and because we need **scoped/compat** builds that a public CDN file does not provide.
- Theme **selection** (Bootstrap vs Bootswatch) is a stylesheet swap, not a Python theme provider object. Swap is per-client (3.9).
- Color **mode** (light/dark/auto) is `data-bs-theme` on the scope-anchor, independent of which Bootswatch file is loaded.
- NiceGUI dark mode is tri-state (`True` / `False` / `None`=auto) and Tailwind’s dark variant follows Quasar `body--dark`. Bootstrap 5.3 uses `data-bs-theme="light"|"dark"` on document or subtree.
- Do **not** assume NiceGUI color tokens equal Bootstrap tokens. Palettes stay independent unless a future mapping table is explicitly added (non-goal for v1).
- All theme CSS is assigned to `layer(overrides)` (3.8).

### 5.2 Asset set

Pinned at build time (Open question 1):

| Asset | Proposed pin |
|---|---|
| Bootstrap CSS (default) | 5.3.8 compiled from upstream Sass, plus scoping |
| Bootswatch themes | Builds compatible with the same Bootstrap minor (Bootswatch documents 5.3.8; DBC 2.0.4 used 5.3.6 URLs) |
| Bootstrap Icons CSS | 1.11.3 |
| Font Awesome CSS | 6.7.2 |
| Reboot / grid-only | `themes.GRID` analogue: grid-only stylesheet like DBC `GRID` |

Also ship `ngbs-compat.css` (Tailwind/Quasar conflict rules) and `ngbs-host.css` (container resets, overlay root). Both injected in `layer(overrides)`.

Sass `$prefix` is **not** used to rename component classes. Variables remain `--bs-*` on the scope-anchor.

Mode B scoper implements the selector map in 3.8.1 (`html`/`body`/` :root` → `.ngbs`, never `.ngbs html`).

### 5.3 `setup()` and `ThemeController`

Revision note (R1): `setup()` is process-level; `ThemeController.for_client()` is page-lifetime.

```python
class StyleMode(enum.Enum):
    BOOTSTRAP_FIRST = "bootstrap-first"
    MIXED = "mixed"

def setup(
    *,
    mode: StyleMode = StyleMode.MIXED,
    theme: object = themes.BOOTSTRAP,
    color_mode: str | None = "auto",     # light|dark|auto|None
    icons: str | None = None,            # bootstrap|fontawesome|None
    cdn: bool = False,                   # default bundled
    follow_nicegui_dark: bool = True,
) -> None: ...

class ThemeController:
    @classmethod
    def for_client(cls) -> "ThemeController":
        """Bind or return the controller for the current NiceGUI client."""
        ...
    def set_color_mode(self, mode: str) -> None: ...
    def set_theme(self, theme: object) -> None: ...
    def bind_to_nicegui_dark(self, enabled: bool = True) -> None: ...
```

Per-page usage:

```python
from nicegui import ui
from nicegui_bootstrap_components import bs, setup, StyleMode, themes, ThemeController

setup(mode=StyleMode.BOOTSTRAP_FIRST, theme=themes.FLATLY, color_mode="auto")

@ui.page("/")
def page() -> None:
    ThemeController.for_client()  # lazy-bind; color_mode default from setup()
    with bs.scope():              # no-op-ish in Mode A; required island in Mode B
        bs.button("Hello", color="primary")
```

`setup()` may be called at import/module level for asset choice; **color_mode auto** is resolved in the browser per client. `set_theme()` uses the per-client `<style id="ngbs-theme-client">@import … layer(overrides)</style>` swap (3.9). First library component in a page also lazy-binds the controller so authors who never mention `ThemeController` still get `data-bs-theme` on the overlay root.

### 5.4 Auto mode algorithm

```
Python color_mode
  "light" → set data-bs-theme=light on scope-anchor + overlay root
  "dark"  → set data-bs-theme=dark
  "auto"  → if follow_nicegui_dark:
                watch Quasar/NiceGUI resolved dark (body.body--dark)
                map True → dark, False → light
            else:
                watch prefers-color-scheme
```

One observer only, owned by the per-client `ThemeController`. Do not let NiceGUI dark and Bootstrap controller fight (no two-way loop). **Proposed default:** library **follows** NiceGUI’s resolved dark state; it does not call `ui.dark_mode()` itself unless the user uses a provided `bs.color_mode_toggle` recipe in docs (clientside, like DBC’s theme guide).

Overlays outside the `.ngbs` subtree still receive `data-bs-theme` on `#ngbs-overlay-root`.

### 5.5 Bootswatch

Treat Bootswatch as a **replacement** stylesheet, not layered on top of Bootstrap core (duplicate Reboot would fight). Each theme is a full build run through the same scoper as default Bootstrap, injected in `layer(overrides)`.

Dark Bootswatch themes (CYBORG, DARKLY, SLATE, SOLAR, SUPERHERO, VAPOR, …) still participate in `data-bs-theme` where the theme supports 5.3 color modes. Visual tests per theme are scheduled, not every PR (Section 8).

Custom themes: `setup(theme="url-or-static-path")` with the requirement that the file is already scoped for Mode B or unscoped for Mode A, and still imported into `layer(overrides)`. Do not promise that setting one CSS variable rebuilds Sass-derived hover/active variants.

### 5.6 Runtime tokens

Document supported runtime tweaks via `--bs-*` on `.ngbs`: `--bs-primary`, `--bs-body-bg`, `--bs-body-color`, etc. Caveat: many component colors are compiled. For a full custom palette, compile Sass (contributor path), not a one-variable override.

### 5.7 DBC theme explorer analogue

Docs include a theme explorer page on the **demo service** (not static Pages) that swaps Bootswatch files and toggles `data-bs-theme`. It is not a Dash clientside callback; it is a NiceGUI page calling `ThemeController.for_client()`.

---

## 6. Documentation architecture

### 6.1 Generator choice

**Proposed default: MkDocs Material + mkdocstrings + a generated contract table plugin + a separately hosted NiceGUI demo service.**

Rationale: GitHub Pages cannot run NiceGUI. DBC’s own site is Flask+Dash hybrid; we should not port that. MkDocs Material is the static shell; live examples are iframes or “Open live” links against `https://demo.<project>/...` versioned by git tag.

Sphinx+MyST is acceptable if the implementation team needs deeper cross-refs; it is not required. **Do not** import NiceGUI’s private `website.*` modules as a public API.

### 6.2 Site map (routes)

Mirror DBC’s page types:

| Page | Path |
|---|---|
| Landing | `/` |
| Quickstart | `/docs/quickstart/` |
| Themes overview | `/docs/themes/` |
| Theme explorer (link out to demo) | `/docs/themes/explorer/` |
| Icons | `/docs/icons/` |
| FAQ | `/docs/faq/` |
| Component index | `/docs/components/` |
| Component family | `/docs/components/<slug>/` |
| Examples index | `/examples/` |
| Example detail | `/examples/<name>/` (static description + screenshot + source; live on demo) |
| Changelog | `/changelog/` |
| Compatibility | `/compatibility/dbc-2.0.4/` |
| Mixed-mode guide | `/guides/mixed-nicegui-pages/` |
| Bindings/events | `/guides/callbacks-and-bindings/` |
| Accessibility | `/guides/accessibility/` |
| Assets/CSP | `/guides/assets-and-csp/` |
| Contributing | `/contributing/` |

Mixed-mode guide must document: `bs.scope`, `layer(overrides)` injection, unlayered-user-CSS tradeoff, Reboot mapping, and the `@layer overrides` escape hatch.

### 6.3 Sidebar taxonomy

**Must include DBC’s exact component slug order** under Components:

```
accordion, alert, badge, breadcrumb, button, button_group, card,
carousel, collapse, dropdown_menu, fade, form, input, input_group,
jumbotron, layout, list_group, modal, nav, navbar, offcanvas,
pagination, placeholder, popover, progress, spinner, table, tabs,
toast, tooltip
```

DBC has **no** Layout/Input/Feedback headings in that list. We **may add** a second nav (“By category”) with Layout, Forms, Navigation, Feedback, Overlays, Utilities — in addition, not as a replacement. Default landing of Components is the DBC order.

Top-level docs nav analogue: Home, Documentation, Examples, More (Changelog, Report a bug, Contribute). Light/Dark/Auto control on the **demo** site; the static docs site uses Material’s color toggle (does not need to drive Bootstrap components except on embedded iframes).

Desktop layout analogue: navigation ~3 cols, content ~9 cols (Material grid is fine; not required to use Bootstrap to document Bootstrap).

### 6.4 Component page template

Each family page:

1. Title + one-paragraph lead (handwritten).
2. Usage introduction.
3. Feature subsections: prose + **live demo** + **exact source** from the same file.
4. Keyword arguments / prop tables **per exported component** on that page (Input page has eight, Layout four, Jumbotron none). Native vs compat differences (extensions) are a column, not a footnote only.
5. Compatibility note (supported / adapted / excluded).
6. Accessibility notes.
7. Related examples.

Handwritten Markdown uses directives (implemented as MkDocs plugin or preprocessor):

```
{{example:examples/components/input/debounce.py:demo}}
{{code-example:examples/components/input/debounce.py}}
{{apidoc:Input}}
{{apidoc:Textarea}}
```

`{{apidoc:Name}}` renders from the **contract JSON + Python signature + docstring**, not from DBC JavaScript at docs runtime (DBC’s `{{apidoc:src/components/...}}` actually reads `getattr(dbc, name).__doc__`).

**Same-source principle:** the file that runs in the demo is the file shown. No copied snippets in Markdown.

Example modules:

```python
# examples/components/button/colors.py
from nicegui import ui
from nicegui_bootstrap_components import bs

def demo() -> None:
    with bs.scope():
        with bs.stack(direction="horizontal", gap=2):
            for color in ("primary", "secondary", "success", "danger"):
                bs.button(color.capitalize(), color=color)

if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Button colors")
```

Docs loader imports `demo` inside a NiceGUI page on the demo host. Static docs show pygments of the same file (optionally only the `demo` function body).

Layout examples that add debug borders must warn, as DBC does, that those utilities are documentation-only.

### 6.5 Prop tables (generated)

Not free-form prose. CI fails if an exported component lacks a page, if a documented prop is missing from the class, or if a DBC 2.0.4 prop lacks a disposition.

Columns:

| Property | Python type | Default | Units | Writable / bindable | Events | DBC 2.0.4 name | Support (native) | Support (compat) |
|---|---|---|---|---|---|---|---|---|

Support values: `supported`, `adapted`, `deprecated-alias`, `extension`, `unsupported`.

Nested dicts (`Col` breakpoint dict, `delay` objects) rendered as sub-rows.

### 6.6 Voice and licensing of docs text

Neutral technical writing. Do not paste DBC documentation verbatim (copyright). Re-explain behavior in original prose. Component semantics may follow DBC; wording must be original. Code examples are written from scratch in NiceGUI idiom.

No generation footers, no tool references, no changelog jokes.

### 6.7 Versioning of docs

Immutable docs per released version (`/en/2.0.0/` or `/v0.1.0/`). Version selector on the site. Addresses the class of need in DBC issue #1164 (old docs hard to find; issue verified 2026-09-20, state open). Compatibility/migration pages link from changed props.

### 6.8 Demo service

- FastAPI/NiceGUI app in `demo/` that registers every example `demo()` on a route derived from the gallery/component manifest.
- Isolated per session (normal NiceGUI client isolation). Resource limits (max elements, no unbounded carousels).
- Lazy load: examples instantiated when requested, not all at process start.
- Screenshots generated in CI for static docs fallback when the demo is down.
- Do not label a JS-only mock as a Python callback example.

---

## 7. Examples gallery blueprint

Three layers, matching DBC’s educational structure — not only three screenshots.

### 7.1 Layer 1 — Component demonstrations

One focused example file per feature, referenced from component pages. Counts need not equal DBC’s 14 Input examples, but each **portable** feature in Section 4 must have at least one: colors, outline, sizes, debounce modes (bool on both surfaces; int debounce on native only), grid breakpoints, dismissible alert, modal static backdrop, accordion `always_open`, tabs without ids, tabs `card=True`, navbar `fixed`/`sticky`, etc.

Location: `examples/components/<slug>/*.py`.

Each file: import-safe `demo()` + `__main__` guard. No extra narrative prints. Mode B examples wrap with `bs.scope()`.

### 7.2 Layer 2 — Hosted gallery (three apps)

Reproduce **purpose**, NiceGUI-native implementation, original code (not a Dash port dump).

| App | Route | Pedagogy | Notes |
|---|---|---|---|
| Iris | `/examples/iris/` | Interactive clustering / filter + visualization of Iris | Use optional plotting extra (Plotly or matplotlib). If Plotly, graphs are NiceGUI `ui.plotly` **outside** the Bootstrap inventory; the page chrome is `bs.*`. Document mixed graph widget. |
| Graphs in Tabs | `/examples/graphs-in-tabs/` | Charts sized correctly when shown in `bs.tabs` | The DBC lesson is graph sizing in hidden panes. Test `display:none` panes vs `ui.plotly`/`echart` resize on tab shown. Call resize on `shown`/tab change. |
| Simple sidebar | `/examples/simple-sidebar/` | Multipage navigation, sidebar, active links | NiceGUI `ui.page` routes; `NavLink.active` from current path. Small-screen warning analogue if the layout collapses. |

Gallery index: title, screenshot card, short description. Cards stack on small screens and sit three-across from `md` (DBC: `col-12 col-md-4`). Detail page: live app **above** a Source Code section (not a tabbed editor). Preview min-height ~700px analogue on the demo host.

### 7.3 Layer 3 — Repository examples and templates

Mirror DBC’s repository breadth:

```
examples/gallery/           # fuller apps (iris, graphs_in_tabs, plus 1–2 extras)
examples/advanced/          # navbars.py, toast.py, graphs_in_tabs.py
examples/templates/         # multi-page:
                            #   simple_sidebar.py
                            #   navbar.py
                            #   responsive_sidebar.py
                            #   responsive_collapsible_sidebar.py
                            #   sidebar_with_submenus.py
                            #   collapsible_sidebar_with_icons.py
```

Extras beyond DBC that teach **this** library (allowed in gallery, labelled “NiceGUI integration” not “DBC clone”):

- Validated form + `FormFeedback`
- Modal confirm (`prevent_close` extension optional)
- Responsive offcanvas nav
- Color-mode toggle following NiceGUI dark
- Toast vs `ui.notify` comparison (docs, not a competing default)
- Mixed Mode B page: `bs.scope` island beside a Quasar `ui.button`

### 7.4 Gallery manifest

`examples/manifest.yaml`:

```yaml
- id: iris
  title: Iris k-means
  route: /examples/iris/
  source: examples/gallery/iris/main.py
  components: [Container, Row, Col, Card, Button, Input, ...]
  extras: [pandas, plotly]
  version: ">=0.1.0"
```

Drives docs index, smoke tests, screenshot jobs, coverage of components-in-examples.

### 7.5 Single-file rule

Public examples are single files unless data assets require a directory (`iris/data.csv`). Templates that must be multi-file (multi-page) use a package with `home.py` / `page2.py` and a `main.py` entry.

Every example runs with:

```
pip install nicegui-bootstrap-components[examples]
python examples/templates/simple_sidebar.py
```

---

## 8. Test strategy

NiceGUI distinguishes **User** (simulated, fast, not real Vue/Bootstrap) from **Screen** (Selenium in NiceGUI core). This library uses User + **Playwright** (Python pytest plugin) for real browser tests. Passing User tests never gates JS behavior.

### 8.1 Four layers

| Layer | Tool | Covers |
|---|---|---|
| L1 Pure Python | pytest | Normalization, aliases, grid mapping, option conversion, children adoption rules, rejected names, manifest completeness, `from_dataframe` without a browser, surface-divergent validation (`bs.Input` vs `dbc.Input`) |
| L2 User | `nicegui.testing.User` | Construction, Python callbacks, value round-trip **as seen by Python**, client isolation, deletion |
| L3 Browser | Playwright | Transitions, focus, keyboard, layout, portals, reconnect, cleanup, CSS collisions, `import('vue')` |
| L4 Visual / a11y | Playwright screenshots + axe-core (or equivalent) on a schedule | Themes, breakpoints, Mode A/B, overlays |

NiceGUI User `.type()` only knows built-in input classes. **Library inputs need helpers** (`element.run_method` or firing the Vue event) — User tests for Input will be limited; debounce belongs in L3.

### 8.2 Project pytest setup

```python
# tests/conftest.py
pytest_plugins = ["nicegui.testing.plugin"]
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
main_file = ""
markers = [
  "user: NiceGUI User fixture",
  "browser: Playwright",
  "visual: screenshot baselines",
]
```

Page functions are route-local; no shared auto-index client (NiceGUI 3 removed it).

### 8.3 L1 examples

- `Col` dicts copied not mutated; `xs` overrides `width`; float `0.5` rejected.
- `class_name` vs `className` precedence; `DeprecationWarning` only on native when both unequal.
- `Fade(is_open=True)` TypeError or unexpected-kw — only `is_in`.
- Removed props `ride`, `Navbar(light=True)` TypeError (absent from signature).
- Accordion `always_open` type of `active_item`.
- Button `external_link` not in rendered attrs when no href.
- `dbc.Input(type="color")` → `UnsupportedPropError`; `bs.input(type="color")` allowed.
- `dbc.DropdownMenu(is_open=True)` → `UnsupportedPropError`; native accepts.
- `dbc.Input(debounce=250)` → `UnsupportedPropError`; native accepts int.
- `from_dataframe(..., index=True)` default (DBC).
- `bs.Button is not dbc.Button`; both have `component_name == "Button"`.
- Manifest: 66 exports, every DBC 2.0.4 prop has per-surface disposition.
- Style dict `{width: 100}` → `100px`; `{opacity: 0.5}` stays unitless.

### 8.4 L2 User example

```python
from nicegui import ui
from nicegui.testing import User
from nicegui_bootstrap_components import bs, setup, StyleMode

async def test_button_click_updates_label(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with bs.scope():
            status = ui.label("Idle")
            bs.button("Apply", on_click=lambda: status.set_text("Applied"))

    await user.open("/")
    user.find("Apply").click()
    await user.should_see("Applied")
```

Also: two `User` clients do not share `n_clicks` or input values.

**L2 (or cheap L3) Vue import guard:** a page with any V component evaluates `await import('vue')` in the browser and asserts the module is the host runtime (constructor/`version` present; URL contains `/_nicegui/` and `vue.esm-browser`). Fails if a future NiceGUI drops the import-map entry.

Value round-trip L2 tests rely on `model-value` / `update:modelValue` (3.5).

### 8.5 L3 browser priorities (must not be “unit-tested away”)

Revision note (R1): L3 color test is a computed-style assertion against `layer(overrides)`; typography-in-`.ngbs` added.

1. Mode B: `.collapse` show/hide is not stuck on Tailwind `visibility: collapse` (computed `visibility` and `display` on a shown/hidden `bs.collapse` panel).
2. Mode B: computed `color` of an element with classes `text-primary` **inside `bs.scope`** equals Bootstrap’s primary token, **not** Quasar’s. Implementation: inject library CSS via `@import … layer(overrides)` with `!important` utilities; read `window.getComputedStyle(el).color`. This test is expected to **pass** under 3.8; if it fails, the injection path is wrong, not the assertion.
3. Mode A: the same `text-primary` computed-color assertion (unscoped Bootstrap still in `layer(overrides)`).
4. Grid: `Col(md=6)` becomes half width at 768px and full at 375px (`xs=12`).
5. **Typography in `.ngbs`:** computed `font-family` of `.btn` and `.form-control` inside `bs.scope` matches Bootstrap Reboot’s body stack (the scope-anchor mapping), **not** Quasar Roboto. Fails if `body` was rewritten to `.ngbs body` (matches nothing, inherit from Quasar) or if Reboot `margin`/`background` was applied to every component root.
6. Input debounce three modes on **native**; compat bool-only; IME if feasible; number empty → `None`.
7. Select option replace; value stringiness; `invalid` class.
8. Modal: open/close, Esc, static backdrop, focus restore, body scroll lock, **delete while open** (no leftover backdrop), rapid toggle converges, children update while open.
9. Two successive modals (policy in 4.14.4).
10. Dropdown keyboard and outside click; no public `is_open` required for DBC usage.
11. Tabs: missing ids, dynamic add/remove, `card=True` markup, graph resize hook.
12. Accordion single vs `always_open` list shape.
13. Tooltip/popover cleanup on target removal; no leaked listeners (page heap / DOM query).
14. Carousel interval + items swap; `slide` class present/absent.
15. Toast default stays open without duration; duration autohides.
16. Theme auto: toggling NiceGUI dark updates `data-bs-theme` on overlay root **while a modal is open** (per-client controller).
17. Reconnect: open modal reconciles.
18. Navbar expand breakpoint: toggler appears/disappears; collapse state; `fixed="top"` class.
19. Reduced motion: collapse/modal doesn’t hang.
20. Wheel install offline: examples run without CDN.
21. `import('vue')` resolves to the host NiceGUI Vue runtime (3.10).
22. Head markup contains `layer(overrides)` for the library stylesheet (string probe on `document.documentElement.innerHTML` or the injected `<style>`).

### 8.6 Visual tests

Revision note (R1): Python Playwright provides `expect(page).to_have_screenshot()`; there is no `expect(page).screenshot()`.

- Use Python Playwright **PageAssertions**: `await expect(page).to_have_screenshot("modal-open.png")` (`from playwright.async_api import expect`). `page.screenshot()` writes bytes/files when a raw capture is needed; it is not an `expect` assertion.
- Freeze OS, browser version, fonts, DPR, viewport in CI (Linux container with DejaVu/Noto).
- Disable CSS animation for static shots; separate tests keep real transitions.
- Never auto-update baselines on main without review.
- A small Node Playwright suite is **not** required for v1 screenshots.

### 8.7 DBC reference harness (optional but tracked)

Dev extra installs `dash-bootstrap-components==2.0.4` for **offline comparison of public values** (e.g. Col class computation, `from_dataframe` cell text, `index=True` default). Not for DOM identity. Do not import Dash at runtime in the library.

### 8.8 CI layout

| Trigger | Jobs |
|---|---|
| Every PR | ruff/format, mypy, L1, L2, manifest check, mkdocs build, example import smoke, Playwright Chromium L3 subset (prototype slice + any changed component) |
| Nightly | min and latest supported NiceGUI, Firefox+WebKit smoke, theme/breakpoint matrix, lifecycle stress, DBC 2.0.5rc canary **without** treating failures as product bugs |
| Release candidate | Build wheel, install in empty venv **without source tree**, offline assets, full L3, license check, visual review |

Record tested versions in `SUPPORT.md`.

### 8.9 Accessibility acceptance (v1 floor)

Not a full WCAG certification claim. Required:

- Controls have names (visible label or `aria-label`).
- Modal focus trap + restore.
- Tabs keyboard.
- Dropdown keyboard.
- `prefers-reduced-motion` honored for collapse/fade/modal.
- Color not the only channel for validation (`FormFeedback` text).
- Tooltips on focus as well as hover when trigger includes focus.

Manual keyboard pass on overlay components before each release.

---

## 9. Packaging and release

### 9.1 Names

| Item | Value |
|---|---|
| PyPI distribution | `nicegui-bootstrap-components` (**availability unconfirmed** — Open question 8) |
| Import | `nicegui_bootstrap_components` |
| Native NS | `nicegui_bootstrap_components.bs` |
| Compat NS | `nicegui_bootstrap_components.dbc` |

PyPI normalizes `_` / `-`; do not ship a second distribution name.

Fallback if the name is taken: `nicegui-bootstrap` then `bootstrap-nicegui`.

### 9.2 Versioning

Semantic versioning on the **public contract** (defaults, events, CSS hooks, compatibility dispositions), not only signatures.

- `0.x` while inventory incomplete.
- `1.0.0` only when Section 2.3 parity gate is met.
- Do not label 0.x “full DBC parity.”

Changelog fragments in `changelog.d/`. Migration notes for observable breaks. PyPI Trusted Publishing.

### 9.3 Python and NiceGUI ranges

Revision note (R1): pin wording unified to “first beta” (was “first alpha” vs OQ17).

Current implementation: the public 0.1.x package uses `nicegui>=3.17.1,<4` rather
than the earlier proposed minor pin. CI runs the non-browser suite against the
minimum and latest available 3.x NiceGUI every push and weekly, while the browser
suite runs against the latest resolver choice. This is a compatibility policy, not
proof of unshipped future versions; a failing canary requires a compatibility fix.

| Constraint | Proposed default |
|---|---|
| Python | `>=3.10,<4` (match NiceGUI 3.17.1). CI 3.10–3.13; add 3.14 when NiceGUI supports it in CI. |
| NiceGUI until first **beta** | `nicegui>=3.17.1,<3.18` |
| NiceGUI after soak | `nicegui>=3.17.1,<4` once nightly against 3.18+ is green |

Dash/DBC are **dev extras** only (`dev` extra pins `dash-bootstrap-components==2.0.4` for the harness).

Optional extras:

```toml
[project.optional-dependencies]
pandas = ["numpy>=2.0.2", "pandas>=2.2.3"]   # align with DBC extra floors unless they conflict with NiceGUI
examples = ["pandas", "plotly"]              # pin in lockfile
dev = ["pytest", "pytest-asyncio", "ruff", "mypy", "playwright", "mkdocs-material", "mkdocstrings[python]", "dash-bootstrap-components==2.0.4"]
```

Runtime install: `pip install nicegui-bootstrap-components` → NiceGUI + bundled assets only.

### 9.4 Package layout

```
src/nicegui_bootstrap_components/
  py.typed
  __init__.py
  bs.py                      # snake_case aliases of native classes
  dbc.py                     # PascalCase compat subclasses + themes/icons aliases
  core.py
  _host.py                   # NiceGUI adapter
  contracts/dbc-2.0.4.json
  components/                # one module per DBC module; private impl + two surfaces
    layout.py
    button.py
    input.py
    ...
  table_dataframe.py
  themes.py
  icons.py
  assets.py
  theme.py
  static/                    # css, js, fonts as needed
  frontend_dist/             # prebuilt Vue esm (externalize vue)
examples/
docs/
demo/
frontend/                    # not in the wheel
styles/                      # not in the wheel (dist copied)
tests/
```

Hatchling backend. Wheel includes Python, JSON contract, `static/`, `frontend_dist/`, license, third-party notices. **Does not** include `frontend/src`.

`py.typed` shipped.

### 9.5 Bootstrap bundling vs CDN

**Default: bundled**, hashed filenames, registered through NiceGUI as `@import url(...) layer(overrides)`. Offline, CSP-friendly (`script-src`/`style-src` for `self`).

CDN: `setup(cdn=True)` uses pinned URLs imported **into `layer(overrides)`** (not a raw `<link>`; SRI on `@import` is weakly supported — document the CSP/SRI limitation and prefer bundled). **Mode B cannot use vanilla CDN Bootstrap** — it would be unscoped. CDN option in Mode B serves **only** if we also host scoped files (not upstream CDN). Therefore:

- Mode A + `cdn=True`: upstream Bootstrap/Bootswatch pinned (like DBC) via `@import … layer(overrides)` + small bundled `ngbs-host.css` in the same layer.
- Mode B: always bundled scoped CSS. `cdn=True` in Mode B raises. **Proposed: raise.**

Do not load full `bootstrap.bundle.js` unless a Plug adapter remains after the prototype. Vue-native path: no Bootstrap JS bundle.

Icons: optional; not injected unless requested (Font Awesome weight is non-trivial).

### 9.6 License

Open question 9. **Proposed default: MIT** (NiceGUI ecosystem, original code). Third-party: Bootstrap (MIT), Bootswatch (MIT), Bootstrap Icons (MIT), Font Awesome (its split license — **document**; consider making FA opt-in CDN-only to simplify wheel license). Include `NOTICE` for bundled CSS.

Do not copy DBC’s generated React/Python sources into the tree (Apache-2.0 would then apply to those files). Reimplementation is original.

### 9.7 README (release)

Screenshot, pip install, 10-line example, support matrix, **explicit compatibility statement** (portable API vs Dash runtime), links to docs/gallery, theming, contributing, license, roadmap. No AI advertising.

### 9.8 Human-authored OSS bar (enforced in review)

- No comments that narrate what the next line does.
- No build-tool watermarks, generation footers, or tool references in the repo (pre-commit grep).
- Examples: conventional comments only (`# iris dataset columns: ...`).
- Docs: original prose.

---

## 10. Implementation plan — ordered phases

Each phase is independently mergeable with tests. Do not start inventory-wide work before phases 0–3 pass.

Revision note (R1): phase 2 no longer requires phase 3 outputs; the prototype uses hand-rolled layered CSS. Phase 3 replaces that CSS with the Sass pipeline and must re-pass phase 2’s browser CSS tests.

---

### Phase 0 — Repository skeleton and policy  
**Acceptance:**

- Hatchling package imports.
- `ruff`, `mypy`, pytest, pre-commit (license/AI-string grep, format).
- `SUPPORT.md`, `CODE_OF_CONDUCT`, Apache/MIT license file as decided.
- Empty `bs`/`dbc` namespaces.
- CI: lint + trivial test.

---

### Phase 1 — Compatibility manifest  
**Acceptance:**

- `contracts/dbc-2.0.4.json` extracted from DBC 2.0.4 as specified in 3.11.
- Script `scripts/extract_dbc_contract.py` documented; re-run is deterministic.
- Every one of 66 components listed with props, defaults, aliases, enums, **per-surface** support.
- Dispositions filled for Dash-only fields.
- Unit test: JSON schema valid; export list length 66.

### Phase 1b — Value-semantics harness  
**Acceptance:**

- Documented notes for Input numeric publishing and Select string values from DBC 2.0.4 source (`Input.js`, `Select.js`) written into the contract `notes` field.
- Confirm DBC `Input.debounce` is boolean; record int-ms as native extension in the JSON.
- No Dash app required if source is conclusive; if not, a minimal Dash harness records values.

---

### Phase 2 — End-to-end prototype (decision gate)

Components: **Container, Row, Col, Button, Input, DropdownMenu, Collapse, Modal, Offcanvas, Tooltip, Toast**, plus native **`bs.scope`**.

Modes: A and B.

**CSS for this phase is hand-rolled and minimal** — not the Sass pipeline (phase 3). Ship a small `prototype-ngbs.css` covering: Reboot `body` font/background mapped onto `.ngbs` per 3.8.1, grid (`container`/`row`/`col-*`), `.btn` / `.form-control` (`font-family: inherit`), `.text-primary` (`!important`), `.collapse` show/hide (`!important`), modal/offcanvas/dropdown/toast/tooltip structure and the z-index table in 3.8.2. Inject **only** via `@import url(...) layer(overrides);` (or `@layer overrides { … }`).

**Acceptance:**

- Wheel install in clean venv, no Node, no network (hand-rolled CSS bundled in the prototype wheel).
- Unrelated Python updates do not corrupt an open Modal/Dropdown.
- Rapid `is_open` toggles converge; delete-while-open cleans backdrop/scroll.
- Two clients independent.
- Keyboard: modal focus trap; dropdown Esc.
- Overlay root carries `data-bs-theme`; a stub in the prototype page (inline, not the full `ThemeController` class) watches `body.body--dark` and updates the overlay root while a modal is open.
- Visual: grid vs a Quasar `ui.button` on the same page in Mode B (island via `bs.scope`).
- Browser tests 8.5.1–8.5.3 and 8.5.5 (collapse, Mode B + Mode A `text-primary` computed color, typography-in-`.ngbs`) **pass** with the hand-rolled sheet.
- `import('vue')` resolves to the host runtime (8.5.21). Head contains `layer(overrides)` (8.5.22).
- `bs.Button is not dbc.Button`; surface-divergent `type="color"` / `debounce=int` checks for Input.
- Written spike report: Tooltip = V or Plug (frozen).
- If CSS coexistence fails in both modes **with layered injection**, **stop** and amend Section 3.8 before continuing.

The decision gate measures cascade-layer correctness, overlay ownership, Vue import, and Tooltip strategy — **not** the production Sass scoper or Bootswatch matrix.

---

### Phase 3 — Asset pipeline and ThemeController  
**Acceptance:**

- Sass build: unscoped + `.ngbs` scoped CSS using the **3.8.1 selector map** (`html`/`body`/` :root` → `.ngbs`, never `.ngbs html`); Bootswatch `FLATLY` and `DARKLY` as samples; remaining themes can be batch in phase 3b.
- Injection remains `@import … layer(overrides)`.
- `setup()` idempotent; Mode B + `cdn=True` raises; conflicting **mode** at process level raises.
- `ThemeController.for_client()`: `data-bs-theme` on scope-anchor and overlay root; per-client stylesheet swap via `#ngbs-theme-client`; follow NiceGUI dark in auto.
- **Re-run phase 2’s browser CSS tests (8.5.1–3, 8.5.5, 8.5.16, 8.5.22) against the Sass output** (hand-rolled prototype CSS is replaced, not kept as the production path).
- Compat CSS for `.collapse` and `.text-primary` as specified in 3.8.3.

### Phase 3b — Remaining Bootswatch + icons constants  
**Acceptance:** All 25 Bootswatch names resolve to bundled files; `themes.GRID`; icons extras.

---

### Phase 4 — Core element infrastructure  
**Acceptance:**

- `BootstrapElementMixin`, `BootstrapElement`, `BootstrapValueElement` (inherits NiceGUI `ValueElement`; frontend `model-value` / `update:modelValue`), overlay element.
- Per-surface sibling subclasses; `_surface` set at construction; L1 tests for divergent validation.
- Children adoption rules with tests (cycle, cross-client, recursive flatten, ambient-slot steal, context-manager vs `children=` conflict, mixed text subset / `ChildrenError` on InputGroup text).
- Public id registry per client.
- Alias precedence `class_name`/`className`.
- Style dict px-ification + unitless allow-list.
- Listener registration only in `__init__` (code review checklist).
- `_host.py` wraps NiceGUI 3.17.1 APIs.

---

### Phase 5 — Layout: Container, Row, Col, Stack  
**Acceptance:** Class mapping table tests; visual breakpoint tests; docs `layout.md` with ≥4 examples; no Quasar row/column usage.

---

### Phase 6 — Actions: Button, ButtonGroup  
**Acceptance:** `n_clicks` + disabled; href/`external_link` DOM leakage test; outline/color matrix; docs.

---

### Phase 7 — Forms structural: Form, Label, FormText, FormFeedback, FormFloating, InputGroup, InputGroupText  
**Acceptance:** Semantic tags; floating-label order documented; submit preventDefault; docs `form` + `input_group`.

---

### Phase 8 — Value controls: Input, Textarea, Select, Checkbox, Switch, RadioButton, Checklist, RadioItems  
**Acceptance:** Debounce bool (both) + int native extension (browser); numeric None; Select strings + `invalid`; group values; User tests where possible; docs `input.md` covering eight components; `type=color` native extension only.

---

### Phase 9 — Content: Badge, Card*, ListGroup*, Table + from_dataframe, Progress, Placeholder  
**Acceptance:** pandas extra optional; multilevel columns test; `from_dataframe` default `index=True`; no `Table.dark`; ListGroup tag fixed at init + contextvar; docs including Jumbotron **recipe** page.

---

### Phase 10 — Nav, NavItem, NavLink, Breadcrumb, Pagination  
**Acceptance:** Active state author-controlled; pagination generated items; mixed phrasing children on NavLink; docs.

---

### Phase 11 — Navbar, NavbarBrand, NavbarToggler, NavbarSimple  
**Acceptance:** Toggler wired to Collapse without Bootstrap data-api; expand breakpoint test; `light` rejected; `fixed`/`sticky` classes; NavbarSimple is composition and forwards `fixed`/`sticky`.

---

### Phase 12 — Tabs / Tab  
**Acceptance:** Generated ids; first-tab default; dynamic children; keyboard; `card=True`; persist analogue optional; docs.

---

### Phase 13 — DropdownMenu / DropdownMenuItem  
**Acceptance:** Internal open state on dbc (`is_open` rejected); direction/menu_variant; headers/dividers; keyboard; native `is_open` extension flagged in manifest.

---

### Phase 14 — Alert, Spinner, Toast  
**Acceptance:** Spinner has no Dash loading probe; Toast default stays open; Toast has no `color` prop; Alert dismiss syncs `is_open`; fullscreen spinner overlay root.

---

### Phase 15 — Collapse, Fade, Accordion*  
**Acceptance:** `is_in` vs `is_open`; `active_item` shape; start_collapsed; reduced motion; Tailwind collapse test reused.

---

### Phase 16 — Modal family + Offcanvas  
**Acceptance:** Styling targets (outer vs dialog); fullscreen enum; static backdrop; focus; one-modal policy; deletion cleanup; offcanvas placements and z-index 1040/1045.

---

### Phase 17 — Tooltip, Popover*  
**Acceptance:** No HTML injection of children; target refs + public ids; cleanup; PopoverHeader/Body are components.

---

### Phase 18 — Carousel  
**Acceptance:** items dicts; active_index 0-based; `ride` rejected (not in signature); `slide` class; interval/pause; items replacement.

---

### Phase 19 — Persistence analogue + navigation analogue  
**Acceptance:** `persist` local/session documented as adapted; requires public `id`; restore does not fire `on_change` and does not write a loop; NavLink internal navigation policy implemented as decided in OQ6.

---

### Phase 20 — Documentation site  
**Acceptance:** MkDocs Material; 30 component slugs; generated prop tables from JSON with per-surface support; same-source examples; versioning layout; original prose; mixed-mode guide covers `layer(overrides)` and `bs.scope`.

---

### Phase 21 — Demo service + Layer 1 examples  
**Acceptance:** Each component page has ≥1 live route; lazy; isolated clients.

---

### Phase 22 — Gallery apps + templates  
**Acceptance:** Iris, Graphs in Tabs (resize on tab shown), Simple sidebar; six templates; manifest smoke.

---

### Phase 23 — Visual/a11y matrix and SUPPORT.md  
**Acceptance:** Baselines for Mode A/B, light/dark, sm/md/lg; axe smoke on overlay pages; keyboard release checklist; `expect(page).to_have_screenshot` baselines.

---

### Phase 24 — 1.0 parity gate  
**Acceptance:** Section 2.3 checklist signed; wheel RC tested offline; changelog; PyPI Trusted Publish dry run; no remaining `TODO` on mandatory props.

---

**Parallelism after phase 4:** 5–6, 7–8, 9 can proceed in parallel; 10–13 nav cluster; 14–18 overlays after overlay service (phase 4+2). Docs (20) can start stubs after phase 1.

---

## 11. Risk register with mitigations

| Rank | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | Bootstrap / Quasar / Tailwind CSS interference (`.collapse`, `.row`, `.text-primary`, resets, Reboot `html`/`body`) | Critical | Two explicit modes; **`layer(overrides)` injection**; scoped build with scope-anchor selector map; compat CSS with `!important`; computed-style browser tests in phase 2 **before** inventory. |
| 2 | Vue and Bootstrap plugins mutate the same DOM | Critical | Vue-owned default; plugin only with inner-node isolation; disable data-api; prototype freeze. |
| 3 | Desired vs actual state divergence (transitions, reconnect, delete-while-open) | Critical | Phase + revision; coalesced commands; reconcile on reconnect; overlay tests. |
| 4 | Overstated “full parity” / Dash semantics leaking | High | Manifest dispositions per surface; 2.3 gate; no callback graph; counters are local, not Dash. |
| 5 | Overlay a11y (focus, stacking, nested modals) | High | One-modal policy; shared overlay root; keyboard tests; no nested modals; z-index table includes offcanvas. |
| 6 | NiceGUI private API churn (3.17.0 routing revert is evidence; verified in 3.17.1 notes) | High | `_host.py` adapter; pin then widen; nightly canaries; `import('vue')` guard. |
| 7 | Input conversion / persistence corrupting values | High | Explicit None/string/number contracts; persist opt-in + id-required; restore does not emit `on_change`; client-keyed storage. |
| 8 | Docs/examples drift from code | High | One example source; generated tables; CI fail on missing apidoc; wheel-based demo. |
| 9 | Assets/CSP/offline/license (Font Awesome) | Medium | Bundled default; FA opt-in; NOTICE; Mode B forbids unscoped CDN; CDN still uses layered `@import`. |
| 10 | Per-client memory and chatty events | Medium | Structural P elements stay cheap; don’t wrap every span; debounce in browser; benchmark gallery pages before 1.0 claims. |
| 11 | Tooltip/popover positioning clipped in `overflow:hidden` parents | Medium | Overlay-root portal when needed (OQ4). |
| 12 | `ui.refreshable` destroying plugin state | Medium | Docs: stable instances; examples don’t rebuild modals via refreshable. |
| 13 | User tests false confidence | Medium | L3 required for JS components; document User limits for custom inputs. |
| 14 | PyPI name collision | Medium | Check before first publish (OQ8); fallback names. |
| 15 | Mixing `ui.notify` (z≈9500) or Quasar menus (z≈6000) with Bootstrap toasts/dropdowns (Mode B overlay root z=5000) | Low/Med | Document “pick one overlay system”; include offcanvas 1040/1045 in the table. |
| 16 | Navbar collapse vs generic Collapse animation | Medium | Dedicated tests at expand breakpoint. |
| 17 | Schema/docs mismatches inherited from DBC (`is_in`, `type=color`, PaginationItem comments) | Low | We implement **declarations**, mention DBC doc bugs in compatibility page. |
| 18 | Multi-worker / multi-process UI | Low | Out of scope; NiceGUI rejects `workers>1` (`ui_run.py:287`). |
| 19 | Desktop pywebview engine quirks | Low | Not a 1.0 gate; revisit later if demanded. |
| 20 | Scope creep (multi-select, nested modals, Quasar restyle) | High | Non-goals; new exports require TDD amendment. |
| 21 | Dual-surface validation silently collapsing | High | Sibling subclasses + `_surface`; L1 tests; manifest per-surface fields. |
| 22 | Unlayered user `!important` cannot override library utilities | Low | Documented tradeoff; escape hatch `@layer overrides`. |

---

## 12. Open questions

Each item has a **proposed default**. Implementers follow the default unless the project owner overrides in writing.

1. **Bootstrap patch version.** DBC 2.0.4 theme URLs pin 5.3.6; current Bootstrap documentation identifies 5.3.8.  
   **Proposed default:** compile **5.3.8** (and matching Bootswatch) for bugfixes; treat visual deltas vs DBC CDN 5.3.6 as acceptable. Record the pin in `assets.py` and `SUPPORT.md`.

2. **Children flattening depth.**  
   **Proposed default:** recursively flatten `list`/`tuple`; drop `None`; error on unknown types.

3. **Public `id` vs DOM `id`.**  
   **Proposed default:** public `id` is a library registry key. It is **also** written to the DOM only when it does not conflict with NiceGUI’s `html_id` scheme; if it would conflict, keep registry-only and use element refs for targets. Overlay `target="foo"` resolves via registry first, then `getElementById`.

4. **Dropdown / popover portal.**  
   **Proposed default:** inline menu unless `in_navbar=True` or it would clip (`detect overflow`); then render in `#ngbs-overlay-root`. Tooltip/popover always in overlay root.

5. **Scope class name.**  
   **Proposed default:** `ngbs` and `ngbs-overlay` on the **scope-anchor only** (`bs.scope` and `#ngbs-overlay-root`). Not user-configurable in v1 (the CSS is compiled against it). Not applied to every component root.

6. **In-app navigation for `href` on NavLink/Button/Breadcrumb.**  
   **Proposed default:** if `external_link=True` or URL is absolute `http(s):`/`mailto:`/`tel:`, use the browser. Else if `href` starts with `/` or is a NiceGUI route, `ui.navigate.to(href)` and `preventDefault`. Else native navigation. Document.

7. **Numeric Input Python type.**  
   **Proposed default:** empty/invalid → `None`; otherwise JSON number → `int` if integral else `float`. Match DBC harness if phase 1b disagrees.

8. **PyPI name availability.**  
   **Proposed default:** `nicegui-bootstrap-components`. Perform a registry check before the first RC; fallback `nicegui-bootstrap`.

9. **License.**  
   **Proposed default:** MIT for original code; FA not bundled in the core wheel (CDN/extra only) to avoid license complexity. Bootstrap/Bootswatch/Bootstrap Icons MIT, bundled with NOTICE.

10. **`setup()` default mode.**  
    **Proposed default:** `StyleMode.MIXED` (safer for existing NiceGUI apps). Quickstart leads with MIXED + `bs.scope`; a “Bootstrap-first app” recipe sets `tailwind=False` + `BOOTSTRAP_FIRST`.

11. **Strictness of unknown compat kwargs.**  
    **Proposed default:** `TypeError` on unknown kwargs (no silent `**kwargs` passthrough to DOM). Prevents prop leakage. Removed props are simply absent.

12. **`key` prop.**  
    **Proposed default:** native — warn once per process, ignore. Compat — `UnsupportedPropError`.

13. **Second modal while one is open.**  
    **Proposed default:** close the first (wait `hidden`), then open the second. No stacking.

14. **Tooltip implementation.**  
    **Proposed default:** Vue + Floating UI, no Bootstrap Tooltip plugin. Freeze after phase 2 if the spike disagrees.

15. **Persist keying.**  
    **Proposed default:** require public `id` for `persist != "off"`; otherwise `ValueError`. Storage key `ngbs:{id}:{prop}`. Restore semantics in 3.9.

16. **Python 3.14 in CI.**  
    **Proposed default:** add when NiceGUI’s own CI supports it; not a 1.0 blocker.

17. **Narrow NiceGUI pin duration.**  
    **Proposed default:** stay on `>=3.17.1,<3.18` until the first **beta**, then widen to `<4` if nightly is green.

18. **`Form` native submit.**  
    **Proposed default:** `prevent_default=True`.

19. **Category nav in docs.**  
    **Proposed default:** extra “By category” section **plus** DBC slug order as primary Components list.

20. **Demo hosting.**  
    **Proposed default:** separate service (Fly/Render/Cloud Run analogue); static docs on GitHub Pages with screenshots and iframe when `DEMO_ORIGIN` is configured. If demo origin unset, show screenshot + source only.

21. **`color` on Input (native).**  
    **Proposed default:** allowed as extension on `bs.Input` / `bs.input`; `UnsupportedPropError` on `dbc.Input` to match 2.0.4 enum. Enforceable because the surfaces are distinct types (3.4.1).

22. **Navbar color / dark mapping under Bootstrap 5.3.**  
    **Proposed default:** map DBC `dark=True` to `data-bs-theme="dark"` on the navbar plus existing `bg-*` classes from `color`; do not resurrect removed `light`. `fixed`/`sticky` are supported (4.13.4).

23. **Whether `bs.button` is a factory or the class, and identity vs `dbc.Button`.**  
    **Proposed default:** `bs.button is bs.Button` (snake_case alias of the **native** sibling subclass). `dbc.Button` is a distinct sibling subclass of the same private impl. They are **not** the same object. See 3.4.1.

24. **Graphs in Tabs plotting library.**  
    **Proposed default:** Plotly via NiceGUI’s plotly integration if `ui.plotly` exists in 3.17.1; else `ui.echart`. Resize on tab `shown`.

25. **Inclusion of DBC issue-driven extras (ship JSON schema).**  
    **Proposed default:** yes, ship `dbc-2.0.4.json` in the wheel under `nicegui_bootstrap_components/contracts/` (motivated by DBC issue #1163, verified 2026-09-20).

26. **`n_clicks` on native API.**  
    **Proposed default:** attribute exists and increments (cheap, aids ports); native docs emphasize `on_click`.

27. **Support for `ui.run(tailwind=False)` documentation vs API to set it.**  
    **Proposed default:** document only; the library never changes the host Tailwind flag.

28. **Accordion item id prop name.**  
    **Proposed default:** follow extracted DBC name (`item_id` vs `id`); native accepts both `item_id` and public `id` with `item_id` winning for accordion state keys.

29. **Minimum browser set.**  
    **Proposed default:** Chromium (CI required), Firefox + WebKit nightly; match “last two versions” of Chrome/Firefox/Safari in SUPPORT.md without claiming exhaustive QA.

30. **Performance budget.**  
    **Proposed default:** no hard FPS claim at 1.0; phase 23 records element counts for gallery pages; investigate if Simple sidebar + 200 nav items drops interaction below usable on the CI machine. No optimization theatre before measurement.

---

### Appendix A — Mapping cheat sheet (implementers)

| DBC | Do |
|---|---|
| React-Bootstrap | Do not depend on it |
| `setProps` | Vue emit → Python prop + handler (`update:modelValue` for values) |
| `className` | Alias of `class_name` |
| `is_open` (Modal, Collapse, Toast, Alert, Offcanvas) | Desired visibility |
| `is_in` (Fade) | Desired visibility (different name) |
| DropdownMenu open | Internal only on dbc; native extension on `bs` |
| Spinner loading API | Explicit `loading` |
| `Table.dark` | Reject |
| Jumbotron | Recipe page |
| themes.py URLs | Names preserved; bundled CSS default in `layer(overrides)` |
| Dash persistence | Opt-in `persist` analogue; id required; no restore `on_change` |
| NiceGUI `ui.button` | Do not subclass |
| Unlayered `<link>` Bootstrap | Do not; use `@import … layer(overrides)` |

### Appendix B — Prototype comparison checklist

Compare the phase 2 slice against standalone Bootstrap 5.3 (same CSS pin) **and** against a DBC 2.0.4 Dash page for: class names on Col/Button/Input/Modal dialog, grid widths at 375/768/1200, modal Esc/focus, dropdown keyboard, computed `text-primary` vs Quasar, `font-family` inside `.ngbs`. DOM need not match React wrappers; **classes, ARIA, and behavior** should.

### Appendix C — File-level comment policy

Public modules: module docstring (one or two sentences). No section banners. Tests: names are the documentation. Frontend: standard SPDX + brief file purpose if the file is not self-explanatory.

---

*End of technical design document.*
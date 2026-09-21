from __future__ import annotations

import hashlib
import json
import re
import sys
import tarfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from tinycss2 import parse_component_value_list, parse_rule_list, parse_stylesheet, serialize

ROOT = Path(__file__).resolve().parents[1]
STYLES_DIR = ROOT / "styles"
SOURCE_CACHE_DIR = STYLES_DIR / "vendor" / "cache"
MANIFEST_PATH = STYLES_DIR / "vendor" / "MANIFEST.json"
STYLE_DIST_DIR = STYLES_DIR / "dist"
PACKAGE_DIST_DIR = ROOT / "src" / "nicegui_bootstrap_components" / "static" / "dist"
PACKAGE_STATIC_DIR = ROOT / "src" / "nicegui_bootstrap_components" / "static"


@dataclass(frozen=True)
class SourceSpec:
    name: str
    upstream_url: str
    version: str
    filename: str
    cache_filename: str
    source_type: str = "archive"
    asset_type: str = "theme"
    style_path: str | None = None
    package_path: str | None = None


_BOOTSTRAP_URL = "https://registry.npmjs.org/bootstrap/-/bootstrap-5.3.8.tgz"
_BOOTSWATCH_URL = "https://registry.npmjs.org/bootswatch/-/bootswatch-5.3.8.tgz"
_BOOTSWATCH_NAMES = (
    "cerulean",
    "cosmo",
    "cyborg",
    "darkly",
    "flatly",
    "journal",
    "litera",
    "lumen",
    "lux",
    "materia",
    "minty",
    "morph",
    "pulse",
    "quartz",
    "sandstone",
    "simplex",
    "sketchy",
    "slate",
    "solar",
    "spacelab",
    "superhero",
    "united",
    "vapor",
    "yeti",
    "zephyr",
)


def _bootswatch_spec(name: str) -> SourceSpec:
    return SourceSpec(
        name=name,
        upstream_url=_BOOTSWATCH_URL,
        version="5.3.8",
        filename=f"package/dist/{name}/bootstrap.css",
        cache_filename=f"bootswatch-5.3.8-{name}.css",
    )


SOURCE_SPECS = (
    SourceSpec(
        name="bootstrap",
        upstream_url=_BOOTSTRAP_URL,
        version="5.3.8",
        filename="package/dist/css/bootstrap.css",
        cache_filename="bootstrap-5.3.8.css",
    ),
    *tuple(_bootswatch_spec(name) for name in _BOOTSWATCH_NAMES),
    SourceSpec(
        name="grid",
        upstream_url=_BOOTSTRAP_URL,
        version="5.3.8",
        filename="package/dist/css/bootstrap-grid.css",
        cache_filename="bootstrap-5.3.8-grid.css",
    ),
)

ICON_CSS_SPECS = (
    SourceSpec(
        name="icon-bootstrap",
        upstream_url=(
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
        ),
        version="1.11.3",
        filename="font/bootstrap-icons.min.css",
        cache_filename="bootstrap-icons-1.11.3.css",
        source_type="direct",
        asset_type="icon_css",
        style_path="dist/ngbs-icons-bootstrap.css",
        package_path="dist/ngbs-icons-bootstrap.css",
    ),
    SourceSpec(
        name="icon-fontawesome",
        upstream_url=(
            "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/css/all.min.css"
        ),
        version="6.7.2",
        filename="css/all.min.css",
        cache_filename="fontawesome-6.7.2.css",
        source_type="direct",
        asset_type="icon_css",
        style_path="dist/ngbs-icons-fontawesome.css",
        package_path="dist/ngbs-icons-fontawesome.css",
    ),
)

ICON_FONT_SPECS = (
    SourceSpec(
        name="font-bootstrap-icons-woff2",
        upstream_url=(
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff2"
        ),
        version="1.11.3",
        filename="font/fonts/bootstrap-icons.woff2",
        cache_filename="bootstrap-icons-1.11.3.woff2",
        source_type="direct",
        asset_type="font",
        style_path="dist/fonts/bootstrap-icons.woff2",
        package_path="dist/fonts/bootstrap-icons.woff2",
    ),
    SourceSpec(
        name="font-bootstrap-icons-woff",
        upstream_url=(
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff"
        ),
        version="1.11.3",
        filename="font/fonts/bootstrap-icons.woff",
        cache_filename="bootstrap-icons-1.11.3.woff",
        source_type="direct",
        asset_type="font",
        style_path="dist/fonts/bootstrap-icons.woff",
        package_path="dist/fonts/bootstrap-icons.woff",
    ),
    *tuple(
        SourceSpec(
            name=f"fontawesome-{font_name}-{extension}",
            upstream_url=(
                "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/"
                f"webfonts/{font_name}.{extension}"
            ),
            version="6.7.2",
            filename=f"webfonts/{font_name}.{extension}",
            cache_filename=f"fontawesome-6.7.2-{font_name}.{extension}",
            source_type="direct",
            asset_type="font",
            package_path=f"webfonts/{font_name}.{extension}",
        )
        for font_name in (
            "fa-brands-400",
            "fa-regular-400",
            "fa-solid-900",
            "fa-v4compatibility",
        )
        for extension in ("woff2", "ttf")
    ),
)

ALL_SOURCE_SPECS = SOURCE_SPECS + ICON_CSS_SPECS + ICON_FONT_SPECS

Z_INDEX_POLICY = """/* Keep overlay layers ordered below the host UI kit's top layer. */
#ngbs-overlay-root { position: relative; z-index: 5000; }
.ngbs .dropdown-menu { --bs-dropdown-zindex: 5000; }
.ngbs .modal { --bs-modal-zindex: 5055; }
.ngbs .modal-backdrop { --bs-backdrop-zindex: 5040; }
.ngbs .offcanvas { --bs-offcanvas-zindex: 5050; }
.ngbs .offcanvas-backdrop { --bs-backdrop-zindex: 5040; }
.ngbs .toast { --bs-toast-zindex: 5090; }
.ngbs .tooltip { --bs-tooltip-zindex: 5090; }"""

COMPAT_SCOPED = """.ngbs .collapse:not(.show), .ngbs-overlay .collapse:not(.show) {
  visibility: visible !important;
  display: none !important;
}
.ngbs .collapse.show, .ngbs-overlay .collapse.show {
  visibility: visible !important;
  display: block !important;
}
.ngbs .collapsing, .ngbs-overlay .collapsing { visibility: visible !important; }
.ngbs .text-primary, .ngbs-overlay .text-primary {
  color: rgba(var(--bs-primary-rgb), var(--bs-text-opacity, 1)) !important;
}"""

COMPAT_UNSCOPED = """.collapse:not(.show) {
  visibility: visible !important;
  display: none !important;
}
.collapse.show {
  visibility: visible !important;
  display: block !important;
}
.collapsing { visibility: visible !important; }
.text-primary {
  color: rgba(var(--bs-primary-rgb), var(--bs-text-opacity, 1)) !important;
}"""

HOST_SCOPED = """/* Keep host flex defaults from changing Bootstrap grid roles. */
.ngbs .container,
.ngbs .row,
.ngbs .col {
  gap: 0;
  padding: 0;
}

/* Overlay z-index policy is part of the scoped theme output. */
"""

HOST_UNSCOPED = """/* Keep host flex defaults from changing Bootstrap grid roles. */
.container,
.row,
.col {
  gap: 0;
  padding: 0;
}

/* Overlay z-index policy is part of the scoped theme output. */
"""


def _is_trivia(token: object) -> bool:
    return getattr(token, "type", None) in {"whitespace", "comment"}


def _split_selector_list(tokens: list[object]) -> list[list[object]]:
    branches: list[list[object]] = [[]]
    for token in tokens:
        if getattr(token, "type", None) == "literal" and getattr(token, "value", None) == ",":
            branches.append([])
        else:
            branches[-1].append(token)
    return branches


def _theme_attribute(token: object) -> bool:
    if getattr(token, "type", None) != "[] block":
        return False
    contents = [part for part in token.content if not _is_trivia(part)]
    if len(contents) not in {3, 4}:
        return False
    if not (
        getattr(contents[0], "type", None) == "ident"
        and getattr(contents[0], "value", "").lower() == "data-bs-theme"
        and getattr(contents[1], "type", None) == "literal"
        and getattr(contents[1], "value", None) == "="
    ):
        return False
    value = getattr(contents[2], "value", "")
    if getattr(contents[2], "type", None) not in {"ident", "string"}:
        return False
    if str(value).lower() not in {"dark", "light"}:
        return False
    if len(contents) == 4:
        return (
            getattr(contents[3], "type", None) == "ident"
            and getattr(contents[3], "value", "").lower() == "i"
        )
    return True


def _prefix(prefix: str, tokens: list[object]) -> list[object]:
    return list(parse_component_value_list(prefix)) + tokens


def _is_literal(token: object, value: str) -> bool:
    return getattr(token, "type", None) == "literal" and getattr(token, "value", None) == value


def _is_ident(token: object, value: str) -> bool:
    return getattr(token, "type", None) == "ident" and getattr(token, "value", "").lower() == value


def _is_root_type(tokens: list[object], index: int) -> bool:
    token = tokens[index]
    if getattr(token, "type", None) != "ident":
        return False
    if getattr(token, "value", "").lower() not in {"html", "body"}:
        return False
    if index == 0:
        return True
    previous = tokens[index - 1]
    return not (
        _is_literal(previous, ".")
        or _is_literal(previous, "#")
        or _is_literal(previous, ":")
        or _is_literal(previous, "|")
    )


def _root_replacement(tokens: list[object], index: int) -> tuple[list[object], int] | None:
    if _is_root_type(tokens, index):
        return list(parse_component_value_list(".ngbs")), 1
    if (
        index + 1 < len(tokens)
        and _is_literal(tokens[index], ":")
        and _is_ident(tokens[index + 1], "root")
    ):
        return list(parse_component_value_list(".ngbs")), 2
    if _theme_attribute(tokens[index]):
        return list(parse_component_value_list(".ngbs")) + [tokens[index]], 1
    return None


def _top_level_anchor_indices(tokens: list[object]) -> list[int]:
    return [
        index
        for index in range(len(tokens) - 1)
        if _is_literal(tokens[index], ".") and _is_ident(tokens[index + 1], "ngbs")
    ]


def _component_end(tokens: list[object], start: int) -> int:
    end = start
    while end < len(tokens):
        token = tokens[end]
        if _is_trivia(token) or (
            getattr(token, "type", None) == "literal"
            and getattr(token, "value", None) in {">", "+", "~", "|"}
        ):
            break
        end += 1
    return end


def _anchor_is_first_in_component(tokens: list[object], index: int) -> bool:
    start = index
    while start > 0:
        token = tokens[start - 1]
        if _is_trivia(token) or (
            getattr(token, "type", None) == "literal"
            and getattr(token, "value", None) in {">", "+", "~", "|"}
        ):
            break
        start -= 1
    return start == index


def _component_has_anchor(tokens: list[object]) -> bool:
    boundary = 0
    for index in range(len(tokens) - 1, -1, -1):
        token = tokens[index]
        if _is_trivia(token) or (
            getattr(token, "type", None) == "literal"
            and getattr(token, "value", None) in {">", "+", "~", "|"}
        ):
            boundary = index + 1
            break
    return any(index >= boundary for index in _top_level_anchor_indices(tokens))


def _theme_attribute_is_root(mapped: list[object]) -> bool:
    if not any(not _is_trivia(token) for token in mapped):
        return True
    if _component_has_anchor(mapped):
        return True
    anchors = _top_level_anchor_indices(mapped)
    if not anchors:
        return False
    last_anchor = anchors[-1]
    return all(_is_trivia(token) for token in mapped[last_anchor + 2 :])


def _collapse_root_chain(tokens: list[object]) -> list[object]:
    anchors = _top_level_anchor_indices(tokens)
    if len(anchors) < 2:
        return tokens
    first = anchors[0]
    first_end = _component_end(tokens, first)
    for second in anchors[1:]:
        if not _anchor_is_first_in_component(tokens, second):
            continue
        separator = tokens[first_end:second]
        if any(
            not (
                _is_trivia(token)
                or (
                    getattr(token, "type", None) == "literal"
                    and getattr(token, "value", None) in {">", "+", "~", "|"}
                )
            )
            for token in separator
        ):
            continue
        del tokens[first_end : second + 2]
        return _collapse_root_chain(tokens)
    return tokens


def _mapped_selector(tokens: list[object]) -> list[object]:
    meaningful = [token for token in tokens if not _is_trivia(token)]
    if not meaningful:
        return tokens
    mapped: list[object] = []
    found_root = False
    index = 0
    while index < len(tokens):
        replacement = _root_replacement(tokens, index)
        if (
            replacement is not None
            and _theme_attribute(tokens[index])
            and not _theme_attribute_is_root(mapped)
        ):
            replacement = None
        if replacement is None:
            mapped.append(tokens[index])
            index += 1
            continue
        replacement_tokens, consumed = replacement
        if _component_has_anchor(mapped):
            if _theme_attribute(tokens[index]):
                mapped.append(tokens[index])
        else:
            mapped.extend(replacement_tokens)
        found_root = True
        index += consumed
    if not found_root:
        return _prefix(".ngbs ", tokens)
    return _collapse_root_chain(mapped)


def _validate_scoped_selector(tokens: list[object]) -> None:
    selector = serialize(tokens).strip()
    if re.search(r"\.ngbs\s+(?:html|body)(?![-\w])", selector):
        raise RuntimeError(f"scoped selector contains a dead root descendant: {selector}")
    anchors = _top_level_anchor_indices(tokens)
    if not anchors:
        return
    meaningful_index = next(
        (index for index, token in enumerate(tokens) if not _is_trivia(token)),
        None,
    )
    if meaningful_index is None or anchors[0] != meaningful_index:
        raise RuntimeError(f"scoped selector places .ngbs below another selector: {selector}")
    if any(_anchor_is_first_in_component(tokens, index) for index in anchors[1:]):
        raise RuntimeError(f"scoped selector contains a descendant .ngbs anchor: {selector}")


def _scope_selector_branch(tokens: list[object]) -> list[object]:
    start = 0
    while start < len(tokens) and _is_trivia(tokens[start]):
        start += 1
    end = len(tokens)
    while end > start and _is_trivia(tokens[end - 1]):
        end -= 1
    if start == end:
        return tokens
    mapped = _mapped_selector(tokens[start:end])
    _validate_scoped_selector(mapped)
    return tokens[:start] + mapped + tokens[end:]


def _scoped_prelude(tokens: list[object]) -> list[object]:
    branches = _split_selector_list(tokens)
    scoped: list[object] = []
    for index, branch in enumerate(branches):
        if index:
            scoped.extend(parse_component_value_list(","))
        scoped.extend(_scope_selector_branch(branch))
    return scoped


def _render_nodes(nodes: list[object]) -> str:
    rendered: list[str] = []
    for node in nodes:
        node_type = getattr(node, "type", None)
        if node_type == "qualified-rule":
            rendered.append(
                serialize(_scoped_prelude(node.prelude)) + "{" + serialize(node.content) + "}"
            )
        elif node_type == "at-rule":
            rendered.append(_render_at_rule(node))
        else:
            rendered.append(serialize([node]))
    return "".join(rendered)


def _render_at_rule(node: object) -> str:
    name = getattr(node, "at_keyword", "").lower()
    content = getattr(node, "content", None)
    if content is None or name.endswith("keyframes") or name == "font-face":
        return serialize([node])

    nested = parse_rule_list(content, skip_whitespace=False, skip_comments=False)
    nested_types = {getattr(item, "type", None) for item in nested}
    if not nested_types.intersection({"qualified-rule", "at-rule"}):
        return serialize([node])
    if "error" in nested_types:
        return serialize([node])
    return "@" + node.at_keyword + serialize(node.prelude) + "{" + _render_nodes(nested) + "}"


def transform_css(css: str) -> str:
    nodes = parse_stylesheet(css, skip_whitespace=False, skip_comments=False)
    return _render_nodes(nodes)


def scope_css(css: str) -> str:
    return transform_css(css)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_SOURCE_MAP_RE = re.compile(r"(?m)^[ \t]*/\*# sourceMappingURL=[^*]*\*/[ \t]*(?:\r?\n|$)")


def _strip_source_maps(css: str) -> str:
    return _SOURCE_MAP_RE.sub("", css)


def _manifest_entries(manifest: object) -> list[dict[str, str]]:
    entries = manifest.get("sources") if isinstance(manifest, dict) else manifest
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise RuntimeError(f"invalid source manifest: {MANIFEST_PATH}")
    return entries


def _read_manifest() -> list[dict[str, str]] | None:
    if not MANIFEST_PATH.is_file():
        return None
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read source manifest: {MANIFEST_PATH}") from exc
    return _manifest_entries(manifest)


_ARCHIVE_CACHE: dict[str, bytes] = {}


def _download_source(spec: SourceSpec) -> bytes:
    if spec.source_type != "direct" and spec.upstream_url in _ARCHIVE_CACHE:
        archive_data = _ARCHIVE_CACHE[spec.upstream_url]
    else:
        request = Request(spec.upstream_url, headers={"User-Agent": "nicegui-bootstrap-components"})
        with urlopen(request, timeout=60) as response:
            source_data = response.read()
        if spec.source_type == "direct":
            return source_data
        _ARCHIVE_CACHE[spec.upstream_url] = source_data
        archive_data = source_data
    with tarfile.open(fileobj=BytesIO(archive_data), mode="r:gz") as archive:
        try:
            member = archive.getmember(spec.filename)
        except KeyError as exc:
            raise RuntimeError(
                f"source file not found in {spec.upstream_url}: {spec.filename}"
            ) from exc
        extracted = archive.extractfile(member)
        if extracted is None:
            raise RuntimeError(f"source file is not readable: {spec.filename}")
        return extracted.read()


def _load_source(spec: SourceSpec) -> bytes:
    cache_path = SOURCE_CACHE_DIR / spec.cache_filename
    if cache_path.is_file():
        return cache_path.read_bytes()
    data = _download_source(spec)
    cache_path.write_bytes(data)
    return data


def _manifest_entry(spec: SourceSpec, digest: str) -> dict[str, str]:
    return {
        "upstream_url": spec.upstream_url,
        "version": spec.version,
        "filename": spec.filename,
        "sha256": digest,
    }


def _write_manifest(entries: list[dict[str, str]]) -> None:
    payload = {"sources": entries}
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _manifest_match(
    entries: list[dict[str, str]] | None,
    spec: SourceSpec,
    digest: str,
) -> None:
    if entries is None:
        return
    matching = [
        entry
        for entry in entries
        if entry.get("upstream_url") == spec.upstream_url
        and entry.get("version") == spec.version
        and entry.get("filename") == spec.filename
    ]
    if len(matching) != 1 or matching[0].get("sha256") != digest:
        if not matching:
            return
        raise RuntimeError(f"source hash does not match the manifest: {spec.filename}")


def _load_sources(specs: tuple[SourceSpec, ...] = ALL_SOURCE_SPECS) -> dict[str, bytes]:
    SOURCE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    STYLE_DIST_DIR.mkdir(parents=True, exist_ok=True)
    PACKAGE_DIST_DIR.mkdir(parents=True, exist_ok=True)
    entries = _read_manifest()
    sources: dict[str, bytes] = {}
    actual_entries: list[dict[str, str]] = []
    for spec in specs:
        data = _load_source(spec)
        digest = _sha256(data)
        actual_entry = _manifest_entry(spec, digest)
        _manifest_match(entries, spec, digest)
        actual_entries.append(actual_entry)
        sources[spec.name] = data
    _write_manifest(actual_entries)
    return sources


def _append_policy(css: str) -> str:
    if not css.endswith("\n"):
        css += "\n"
    return css + "\n" + Z_INDEX_POLICY + "\n"


def _write_pair(filename: str, data: bytes) -> None:
    (STYLE_DIST_DIR / filename).write_bytes(data)
    (PACKAGE_DIST_DIR / filename).write_bytes(data)


def _write_asset(spec: SourceSpec, data: bytes) -> None:
    for root, relative_path in (
        (STYLES_DIR, spec.style_path),
        (PACKAGE_STATIC_DIR, spec.package_path),
    ):
        if relative_path is None:
            continue
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def build() -> None:
    SOURCE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    STYLE_DIST_DIR.mkdir(parents=True, exist_ok=True)
    PACKAGE_DIST_DIR.mkdir(parents=True, exist_ok=True)
    entries = _read_manifest()
    actual_entries: list[dict[str, str]] = []
    for spec in ALL_SOURCE_SPECS:
        source = _load_source(spec)
        digest = _sha256(source)
        _manifest_match(entries, spec, digest)
        actual_entries.append(_manifest_entry(spec, digest))
        if spec.asset_type == "theme":
            text = _strip_source_maps(source.decode("utf-8"))
            _write_pair(
                f"ngbs-{spec.name}.css",
                _append_policy(scope_css(text)).encode("utf-8"),
            )
            _write_pair(f"ngbs-{spec.name}-unscoped.css", text.encode("utf-8"))
        else:
            _write_asset(spec, source)
    _write_pair("ngbs-compat.css", (COMPAT_SCOPED + "\n").encode("utf-8"))
    _write_pair("ngbs-compat-unscoped.css", (COMPAT_UNSCOPED + "\n").encode("utf-8"))
    _write_pair("ngbs-host.css", HOST_SCOPED.encode("utf-8"))
    _write_pair("ngbs-host-unscoped.css", HOST_UNSCOPED.encode("utf-8"))
    _write_manifest(actual_entries)


def main() -> int:
    try:
        build()
    except (OSError, RuntimeError, UnicodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

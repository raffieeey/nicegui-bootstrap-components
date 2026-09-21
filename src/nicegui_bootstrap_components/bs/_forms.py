"""Forms family: Form, Label, FormText, FormFeedback, FormFloating, InputGroup, InputGroupText."""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any

from .._base import BootstrapElement, UnsupportedPropError, make_surface_classes
from ._layout import col_breakpoint_classes

__all__ = [
    "DbcForm",
    "DbcFormFeedback",
    "DbcFormFloating",
    "DbcFormText",
    "DbcInputGroup",
    "DbcInputGroupText",
    "DbcLabel",
    "Form",
    "FormFeedback",
    "FormFloating",
    "FormText",
    "InputGroup",
    "InputGroupText",
    "Label",
    "form",
    "form_feedback",
    "form_feedback_classes",
    "form_floating",
    "form_method",
    "form_text",
    "form_text_classes",
    "input_group",
    "input_group_classes",
    "input_group_text",
    "label",
    "label_classes",
]

_FORM_METHODS = frozenset({"GET", "POST"})
_FEEDBACK_TYPES = frozenset({"valid", "invalid"})
_SIZES = frozenset({"sm", "md", "lg"})
_COMPACT_SIZES = frozenset({"sm", "lg"})
_LABEL_ALIGN = frozenset({"start", "center", "end"})

_JS_SUBMIT = """(...args) => {
  const e = args[0];
  if (e && typeof e.preventDefault === 'function') {
    e.preventDefault();
  }
  emit(true);
}"""

_JS_SUBMIT_ALLOW = """(...args) => {
  emit(true);
}"""


def form_method(method: str | None) -> str | None:
    """Validate Form ``method`` (``GET`` or ``POST``) and return it."""
    if method is None:
        return None
    if method not in _FORM_METHODS:
        raise ValueError(f"Invalid Form method: {method!r}")
    return method


def label_classes(
    *,
    size: str | None = None,
    hidden: bool = False,
    check: bool = False,
    color: str | None = None,
) -> list[str]:
    """Return Bootstrap ``form-label`` classes."""
    classes = ["form-label"]
    if hidden:
        classes.append("visually-hidden")
    if size in _COMPACT_SIZES:
        classes.append("col-form-label")
        classes.append(f"col-form-label-{size}")
    elif size not in (None, "md"):
        raise ValueError(f"Invalid Label size: {size!r}")
    if check:
        classes.append("form-check-label")
    if color is not None:
        classes.append(f"text-{color}")
    return classes


def _label_grid_classes(
    *,
    width: object = None,
    xs: object = None,
    sm: object = None,
    md: object = None,
    lg: object = None,
    xl: object = None,
    xxl: object = None,
    align: str | None = None,
) -> list[str]:
    if all(value is None for value in (width, xs, sm, md, lg, xl, xxl)):
        return []
    classes = col_breakpoint_classes(
        width=width,
        xs=xs,
        sm=sm,
        md=md,
        lg=lg,
        xl=xl,
        xxl=xxl,
    )
    if align is not None:
        if align not in _LABEL_ALIGN:
            raise ValueError(f"Invalid Label align: {align!r}")
        classes.append(f"align-self-{align}")
    return classes


def form_text_classes(*, color: str | None = None) -> list[str]:
    """Return Bootstrap ``form-text`` classes."""
    classes = ["form-text"]
    if color is not None:
        classes.append(f"text-{color}")
    return classes


def form_feedback_classes(
    *,
    type: str | None = None,
    tooltip: bool = False,
) -> list[str]:
    """Return Bootstrap valid/invalid feedback or tooltip classes."""
    if type is None:
        return []
    if type not in _FEEDBACK_TYPES:
        raise ValueError(f"Invalid FormFeedback type: {type!r}")
    kind = "tooltip" if tooltip else "feedback"
    return [f"{type}-{kind}"]


def input_group_classes(*, size: str | None = None) -> list[str]:
    """Return Bootstrap ``input-group`` classes."""
    classes = ["input-group"]
    if size in _COMPACT_SIZES:
        classes.append(f"input-group-{size}")
    elif size not in (None, "md"):
        raise ValueError(f"Invalid InputGroup size: {size!r}")
    return classes


def _apply_html_for_to_first_label(host: Any, html_for: str) -> None:
    """Set ``for`` on the first adopted child whose tag is ``label``."""
    slot = getattr(host, "default_slot", None)
    adopted: Any = getattr(slot, "children", None) if slot is not None else None
    if adopted is None:
        adopted = getattr(host, "elements", None)
    if not adopted:
        return
    for child in adopted:
        if getattr(child, "tag", None) == "label":
            props = getattr(child, "_props", None)
            if props is not None:
                props["for"] = html_for
            break


class _FormImpl(BootstrapElement):
    """Private Form implementation. Submit listener is registered in ``__init__`` only."""

    component_name = "Form"
    children_kind = "auto"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        action: str | None = None,
        method: str | None = None,
        prevent_default_on_submit: bool = True,
        n_submit: int = 0,
        novalidate: bool = False,
        on_submit: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        method = form_method(method)
        if self._surface == "compat" and novalidate:
            raise UnsupportedPropError("novalidate")
        self._structural_classes = ()
        self._n_submit = int(n_submit)
        self._on_submit = on_submit
        super().__init__(children, tag="form", **kwargs)
        if action is not None:
            self._props["action"] = action
        if method is not None:
            self._props["method"] = method
        if novalidate:
            self._props["novalidate"] = True
        self._props["data-ngbs-prevent-default"] = "true" if prevent_default_on_submit else "false"
        js_handler = _JS_SUBMIT if prevent_default_on_submit else _JS_SUBMIT_ALLOW
        self.on("submit", self._handle_submit, js_handler=js_handler)

    @property
    def n_submit(self) -> int:
        """Number of times the form was submitted."""
        return self._n_submit

    def _handle_submit(self, *_args: Any, **_kwargs: Any) -> None:
        self._n_submit += 1
        if self._on_submit is not None:
            self._on_submit()


class _LabelImpl(BootstrapElement):
    """Private Label implementation."""

    component_name = "Label"
    children_kind = "auto"
    reserved_classes = ("form-label",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        size: str | None = None,
        html_for: str | None = None,
        hidden: bool = False,
        check: bool = False,
        align: str | None = None,
        color: str | None = None,
        width: object = None,
        xs: object = None,
        sm: object = None,
        md: object = None,
        lg: object = None,
        xl: object = None,
        xxl: object = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            label_classes(size=size, hidden=hidden, check=check, color=color)
            + _label_grid_classes(
                width=width,
                xs=xs,
                sm=sm,
                md=md,
                lg=lg,
                xl=xl,
                xxl=xxl,
                align=align,
            )
        )
        super().__init__(children, tag="label", **kwargs)
        if html_for is not None:
            self._props["for"] = html_for


class _FormTextImpl(BootstrapElement):
    """Private FormText implementation."""

    component_name = "FormText"
    children_kind = "auto"
    reserved_classes = ("form-text",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        color: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(form_text_classes(color=color))
        super().__init__(children, tag="small", **kwargs)


class _FormFeedbackImpl(BootstrapElement):
    """Private FormFeedback implementation."""

    component_name = "FormFeedback"
    children_kind = "auto"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        type: str | None = None,
        tooltip: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(form_feedback_classes(type=type, tooltip=tooltip))
        super().__init__(children, tag="div", **kwargs)


class _FormFloatingImpl(BootstrapElement):
    """Private FormFloating. Control-then-label child order is required; not reordered."""

    component_name = "FormFloating"
    children_kind = "auto"
    reserved_classes = ("form-floating",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        html_for: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = ("form-floating",)
        super().__init__(children, tag="div", **kwargs)
        if html_for is not None:
            with contextlib.suppress(Exception):
                _apply_html_for_to_first_label(self, html_for)


class _InputGroupImpl(BootstrapElement):
    """Private InputGroup implementation."""

    component_name = "InputGroup"
    children_kind = "grouping"
    reserved_classes = ("input-group",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        size: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(input_group_classes(size=size))
        super().__init__(children, tag="div", **kwargs)


class _InputGroupTextImpl(BootstrapElement):
    """Private InputGroupText implementation."""

    component_name = "InputGroupText"
    children_kind = "auto"
    reserved_classes = ("input-group-text",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = ("input-group-text",)
        super().__init__(children, tag="span", **kwargs)


Form, DbcForm = make_surface_classes("Form", globals())
form = Form
Label, DbcLabel = make_surface_classes("Label", globals())
label = Label
FormText, DbcFormText = make_surface_classes("FormText", globals())
form_text = FormText
FormFeedback, DbcFormFeedback = make_surface_classes("FormFeedback", globals())
form_feedback = FormFeedback
FormFloating, DbcFormFloating = make_surface_classes("FormFloating", globals())
form_floating = FormFloating
InputGroup, DbcInputGroup = make_surface_classes("InputGroup", globals())
input_group = InputGroup
InputGroupText, DbcInputGroupText = make_surface_classes("InputGroupText", globals())
input_group_text = InputGroupText

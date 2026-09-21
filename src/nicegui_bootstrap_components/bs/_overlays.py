"""Bootstrap overlay components and their shared browser runtime."""

from __future__ import annotations

import contextlib
import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from nicegui import ui

from .._base import (
    BootstrapElement,
    BootstrapElementMixin,
    ChildrenError,
    PropConflictError,
    UnsupportedPropError,
    make_surface_classes,
)
from .._host import set_element_text

if TYPE_CHECKING:

    def ensure_overlay_root() -> Any: ...
else:
    try:
        from ._overlay_root import ensure_overlay_root
    except ImportError:  # pragma: no cover

        def ensure_overlay_root() -> Any:
            return None


_UNSET = object()

_DIRECTION_CLASS = {
    "down": "dropdown",
    "up": "dropup",
    "start": "dropstart",
    "end": "dropend",
    "left": "dropstart",
    "right": "dropend",
}

_DROPDOWN_COLORS = frozenset(
    {"primary", "secondary", "success", "danger", "warning", "info", "light", "dark", "link"}
)
_DROPDOWN_SIZES = frozenset({"sm", "lg"})
_COLLAPSE_DIMENSIONS = frozenset({"height", "width"})
_OFFCANVAS_PLACEMENTS = frozenset({"start", "end", "top", "bottom"})
_MODAL_SIZES = frozenset({"sm", "lg", "xl"})
_MENU_VARIANTS = frozenset({"light", "dark"})


def dropdown_direction_class(direction: str) -> str:
    """Return the Bootstrap direction class for a dropdown."""
    if direction not in _DIRECTION_CLASS:
        raise ValueError(f"Unsupported DropdownMenu direction={direction!r}")
    return _DIRECTION_CLASS[direction]


def dropdown_root_classes(
    *,
    direction: str = "down",
    nav: bool = False,
    group: bool = False,
    in_navbar: bool = False,
) -> list[str]:
    """Return structural classes for the dropdown root."""
    direction_cls = dropdown_direction_class(direction)
    classes: list[str] = []
    if group:
        classes.append("btn-group")
        if direction != "down":
            classes.append(direction_cls)
    else:
        classes.append(direction_cls)
    if nav or in_navbar:
        classes.append("nav-item")
    return classes


def dropdown_toggle_classes(
    *,
    color: str = "secondary",
    size: str | None = None,
    caret: bool = True,
    nav: bool = False,
) -> list[str]:
    """Return Bootstrap classes for a dropdown toggle."""
    if color not in _DROPDOWN_COLORS:
        raise ValueError(f"Unsupported DropdownMenu color={color!r}")
    if size is not None and size not in _DROPDOWN_SIZES:
        raise ValueError(f"Unsupported DropdownMenu size={size!r}")
    if nav:
        classes = ["nav-link"]
        if caret:
            classes.append("dropdown-toggle")
        return classes
    classes = ["btn"]
    classes.append("btn-link" if color == "link" else f"btn-{color}")
    if size is not None:
        classes.append(f"btn-{size}")
    if caret:
        classes.append("dropdown-toggle")
    return classes


def dropdown_menu_classes(
    *,
    menu_variant: str | None = None,
    align_end: bool | None = None,
) -> list[str]:
    """Return Bootstrap classes for the dropdown menu list."""
    classes = ["dropdown-menu"]
    if menu_variant is not None:
        if menu_variant not in _MENU_VARIANTS:
            raise ValueError(f"Unsupported DropdownMenu menu_variant={menu_variant!r}")
        if menu_variant == "dark":
            classes.append("dropdown-menu-dark")
    if align_end:
        classes.append("dropdown-menu-end")
    return classes


def dropdown_item_inner_classes(
    *,
    header: bool = False,
    divider: bool = False,
    disabled: bool = False,
    active: bool = False,
) -> list[str]:
    """Return Bootstrap classes for the inner dropdown item node."""
    if divider:
        return ["dropdown-divider"]
    if header:
        return ["dropdown-header"]
    classes = ["dropdown-item"]
    if disabled:
        classes.append("disabled")
    if active:
        classes.append("active")
    return classes


def collapse_structural_classes(*, navbar: bool = False, dimension: str = "height") -> list[str]:
    """Return Bootstrap ``collapse`` classes."""
    if dimension not in _COLLAPSE_DIMENSIONS:
        raise ValueError(f"Unsupported Collapse dimension={dimension!r}")
    classes = ["collapse"]
    if dimension == "width":
        classes.append("collapse-horizontal")
    if navbar:
        classes.append("navbar-collapse")
    return classes


def fade_structural_classes(*, is_in: bool = False) -> list[str]:
    """Return Bootstrap ``fade`` classes."""
    classes = ["fade"]
    if is_in:
        classes.append("show")
    return classes


def accordion_structural_classes(*, flush: bool = False) -> list[str]:
    """Return Bootstrap ``accordion`` classes."""
    classes = ["accordion"]
    if flush:
        classes.append("accordion-flush")
    return classes


def modal_dialog_classes(
    *,
    size: str | None = None,
    centered: bool = False,
    scrollable: bool = False,
    fullscreen: bool | str = False,
    dialog_class_name: str | None = None,
) -> list[str]:
    """Return Bootstrap classes for the modal dialog wrapper."""
    classes = ["modal-dialog"]
    if size in _MODAL_SIZES:
        classes.append(f"modal-{size}")
    if centered:
        classes.append("modal-dialog-centered")
    if scrollable:
        classes.append("modal-dialog-scrollable")
    if fullscreen is True:
        classes.append("modal-fullscreen")
    elif isinstance(fullscreen, str) and fullscreen:
        token = (
            fullscreen
            if fullscreen.startswith("modal-fullscreen")
            else f"modal-fullscreen-{fullscreen}"
        )
        classes.append(token)
    if dialog_class_name:
        classes.append(dialog_class_name)
    return classes


def offcanvas_structural_classes(*, placement: str) -> list[str]:
    """Return Bootstrap ``offcanvas`` classes for a placement."""
    if placement not in _OFFCANVAS_PLACEMENTS:
        raise ValueError(f"Offcanvas placement must be start|end|top|bottom, got {placement!r}")
    return ["offcanvas", f"offcanvas-{placement}"]


def generate_accordion_item_ids(given: list[str | None]) -> list[str]:
    """Assign stable ``item-N`` ids without colliding with public ids."""
    used: set[str] = {ident for ident in given if ident}
    result: list[str] = []
    n = 0
    for ident in given:
        if ident:
            result.append(ident)
            continue
        while f"item-{n}" in used:
            n += 1
        fresh = f"item-{n}"
        used.add(fresh)
        result.append(fresh)
        n += 1
    return result


def resolve_accordion_active(
    active_item: str | list[str] | None,
    *,
    always_open: bool,
    item_ids: list[str],
    default_first: bool = False,
) -> str | list[str] | None:
    """Normalize accordion selection to a scalar or list matching ``always_open``."""
    known = set(item_ids)
    if always_open:
        if active_item is None:
            return [item_ids[0]] if default_first and item_ids else []
        values = active_item if isinstance(active_item, list) else [active_item]
        return [ident for ident in values if ident in known]
    if isinstance(active_item, list):
        for ident in active_item:
            if ident in known:
                return ident
        active_item = None
    if active_item is None:
        return item_ids[0] if default_first and item_ids else None
    return active_item if active_item in known else None


_RUNTIME_READY = False

_OVERLAY_CSS = """
#ngbs-overlay-root.ngbs-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-color: transparent;
  z-index: 5000;
}
#ngbs-overlay-root.ngbs-overlay > * { pointer-events: auto; }
#ngbs-overlay-root .dropdown-menu {
  display: none;
  position: absolute;
  z-index: var(--bs-dropdown-zindex);
}
#ngbs-overlay-root .dropdown-menu.show { display: block; }
.ngbs .dropdown, .ngbs .dropup, .ngbs .dropstart, .ngbs .dropend { position: relative; }
.ngbs .dropdown-menu {
  display: none;
  position: absolute;
  z-index: var(--bs-dropdown-zindex);
}
.ngbs .dropdown-menu.show { display: block; }
#ngbs-overlay-root .modal { position: fixed; inset: 0; z-index: var(--bs-modal-zindex); display: none; overflow-x: hidden;
  overflow-y: auto; outline: 0; }
#ngbs-overlay-root .modal.show { display: block; }
#ngbs-overlay-root .modal-dialog { position: relative; width: auto; margin: 1.75rem auto; max-width: 500px;
  pointer-events: none; }
#ngbs-overlay-root .modal-dialog-centered { display: flex; align-items: center; min-height: calc(100% - 3.5rem); }
#ngbs-overlay-root .modal-dialog-scrollable { max-height: calc(100% - 3.5rem); overflow: hidden; }
#ngbs-overlay-root .modal-dialog-scrollable .modal-content { max-height: 100%; overflow: hidden; display: flex;
  flex-direction: column; }
#ngbs-overlay-root .modal-sm { max-width: 300px; }
#ngbs-overlay-root .modal-lg { max-width: 800px; }
#ngbs-overlay-root .modal-xl { max-width: 1140px; }
#ngbs-overlay-root .modal-fullscreen { width: 100vw; max-width: none; height: 100%; margin: 0; }
#ngbs-overlay-root .modal-content { pointer-events: auto; position: relative; outline: 0; }
#ngbs-overlay-root .modal-backdrop { position: fixed; inset: 0; z-index: var(--bs-backdrop-zindex); }
#ngbs-overlay-root .offcanvas { position: fixed; z-index: var(--bs-offcanvas-zindex); display: flex; flex-direction: column;
  outline: 0; }
#ngbs-overlay-root .offcanvas-start { top: 0; left: 0; bottom: 0; width: 400px; max-width: 100%;
  transform: translateX(-100%); }
#ngbs-overlay-root .offcanvas-end { top: 0; right: 0; bottom: 0; width: 400px; max-width: 100%;
  transform: translateX(100%); }
#ngbs-overlay-root .offcanvas-top { top: 0; left: 0; right: 0; height: 30vh; transform: translateY(-100%); }
#ngbs-overlay-root .offcanvas-bottom { bottom: 0; left: 0; right: 0; height: 30vh; transform: translateY(100%); }
#ngbs-overlay-root .offcanvas.show { transform: none; }
#ngbs-overlay-root .offcanvas-backdrop { position: fixed; inset: 0; z-index: var(--bs-backdrop-zindex); }
#ngbs-overlay-root .toast { z-index: var(--bs-toast-zindex); display: none; }
#ngbs-overlay-root .toast.show { display: block; }
#ngbs-overlay-root .tooltip { z-index: var(--bs-tooltip-zindex); position: fixed; display: none; padding: 0.25rem 0.5rem; }
#ngbs-overlay-root .tooltip.show { display: block; }
"""

_OVERLAY_JS = r"""
(function() {
  if (window.__ngbsOverlayProto) return;
  window.__ngbsOverlayProto = 1;

  function overlayRoot() {
    var r = document.getElementById('ngbs-overlay-root');
    if (!r) {
      r = document.createElement('div');
      r.id = 'ngbs-overlay-root';
      r.className = 'ngbs ngbs-overlay';
      document.body.appendChild(r);
    }
    return r;
  }
  window.ngbsEnsureOverlayRoot = overlayRoot;

  if (!window.bootstrap) window.bootstrap = {};

  function focusables(root) {
    var nodes = root.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    return Array.prototype.filter.call(nodes, function(el) {
      return !el.hasAttribute('disabled') && el.getAttribute('aria-hidden') !== 'true';
    });
  }

  function dispatch(el, type) {
    try { el.dispatchEvent(new CustomEvent(type, { bubbles: true })); } catch (err) {}
  }

  var backdropSequence = 0;

  function backdropKey(el) {
    if (!el._ngbsBackdropKey) {
      backdropSequence += 1;
      el._ngbsBackdropKey = 'ngbs-backdrop-' + backdropSequence;
    }
    return el._ngbsBackdropKey;
  }

  function backdropFor(el, kind) {
    var key = backdropKey(el);
    var cls = kind === 'offcanvas' ? 'offcanvas-backdrop' : 'modal-backdrop';
    var b = document.querySelector('[data-ngbs-backdrop="' + key + '"]');
    if (!b) {
      b = document.createElement('div');
      b.className = cls + ' fade show';
      b.setAttribute('data-ngbs-backdrop', key);
      var extraClass = el.getAttribute('data-ngbs-backdrop-class');
      if (extraClass) b.classList.add.apply(b.classList, extraClass.split(/\s+/).filter(Boolean));
      var extraStyle = el.getAttribute('data-ngbs-backdrop-style');
      if (extraStyle) b.style.cssText += ';' + extraStyle;
      overlayRoot().appendChild(b);
    }
    return b;
  }

  function removeBackdrop(el) {
    var key = el._ngbsBackdropKey;
    if (!key) return;
    var b = document.querySelector('[data-ngbs-backdrop="' + key + '"]');
    if (b) b.remove();
    el._ngbsBackdropKey = null;
  }

  function lockBodyScroll(el) {
    if (el._ngbsScrollLocked) return;
    var body = document.body;
    var state = body._ngbsScrollLock;
    if (!state) {
      state = {
        count: 0,
        previousOverflow: body.style.overflow,
        previousModalOpen: body.classList.contains('modal-open'),
        lockedOverflow: 'hidden'
      };
      body._ngbsScrollLock = state;
    }
    state.count += 1;
    el._ngbsScrollLocked = true;
    body.classList.add('modal-open');
    body.style.overflow = state.lockedOverflow;
  }

  function unlockBodyScroll(el) {
    if (!el._ngbsScrollLocked) return;
    el._ngbsScrollLocked = false;
    var body = document.body;
    var state = body._ngbsScrollLock;
    if (!state) return;
    state.count = Math.max(0, state.count - 1);
    if (state.count > 0) return;
    if (body.style.overflow === state.lockedOverflow) {
      if (state.previousOverflow) body.style.overflow = state.previousOverflow;
      else body.style.removeProperty('overflow');
    }
    if (!state.previousModalOpen) body.classList.remove('modal-open');
    delete body._ngbsScrollLock;
  }

  function restoreFocus(el) {
    if (el._ngbsPrevFocus && el._ngbsPrevFocus.focus) {
      try { el._ngbsPrevFocus.focus(); } catch (err) {}
    }
    el._ngbsPrevFocus = null;
  }

  function portal(el) {
    if (el.getAttribute('data-ngbs-portal') === 'true' && el.parentElement !== overlayRoot()) {
      overlayRoot().appendChild(el);
    }
  }

  function NgbsModal(el, opts) {
    this._el = el;
    this._opts = Object.assign({ backdrop: true, keyboard: true, focus: true }, opts || {});
  }
  NgbsModal.prototype.show = function() { showModal(this._el); };
  NgbsModal.prototype.hide = function() { hideModal(this._el); };
  NgbsModal.prototype.toggle = function() {
    if (this._el.classList.contains('show')) this.hide(); else this.show();
  };
  NgbsModal.prototype.dispose = function() { disposeEl(this._el); };
  NgbsModal.getOrCreateInstance = function(el, opts) {
    el._ngbsModal = el._ngbsModal || new NgbsModal(el, opts);
    return el._ngbsModal;
  };
  NgbsModal.getInstance = function(el) { return el._ngbsModal || null; };
  if (!window.bootstrap.Modal) window.bootstrap.Modal = NgbsModal;

  function NgbsCollapse(el) { this._el = el; }
  NgbsCollapse.prototype.show = function() { showCollapse(this._el); };
  NgbsCollapse.prototype.hide = function() { hideCollapse(this._el); };
  NgbsCollapse.prototype.toggle = function() {
    if (this._el.classList.contains('show')) this.hide(); else this.show();
  };
  NgbsCollapse.prototype.dispose = function() {};
  NgbsCollapse.getOrCreateInstance = function(el) {
    el._ngbsCollapse = el._ngbsCollapse || new NgbsCollapse(el);
    return el._ngbsCollapse;
  };
  if (!window.bootstrap.Collapse) window.bootstrap.Collapse = NgbsCollapse;

  function NgbsOffcanvas(el) { this._el = el; }
  NgbsOffcanvas.prototype.show = function() { showOffcanvas(this._el); };
  NgbsOffcanvas.prototype.hide = function() { hideOffcanvas(this._el); };
  NgbsOffcanvas.prototype.toggle = function() {
    if (this._el.classList.contains('show')) this.hide(); else this.show();
  };
  NgbsOffcanvas.prototype.dispose = function() { disposeEl(this._el); };
  NgbsOffcanvas.getOrCreateInstance = function(el) {
    el._ngbsOffcanvas = el._ngbsOffcanvas || new NgbsOffcanvas(el);
    return el._ngbsOffcanvas;
  };
  if (!window.bootstrap.Offcanvas) window.bootstrap.Offcanvas = NgbsOffcanvas;

  function NgbsTooltip(target, cfg) {
    this._target = target;
    this._cfg = cfg || {};
  }
  NgbsTooltip.prototype.show = function() {};
  NgbsTooltip.prototype.hide = function() {
    if (this._tip && this._tip.classList.contains('show')) this._tip.classList.remove('show');
  };
  NgbsTooltip.prototype.dispose = function() {
    if (this._tip && this._tip.remove) this._tip.remove();
    this._tip = null;
  };
  NgbsTooltip.getOrCreateInstance = function(target, cfg) {
    target._ngbsTooltip = target._ngbsTooltip || new NgbsTooltip(target, cfg);
    return target._ngbsTooltip;
  };
  if (!window.bootstrap.Tooltip) window.bootstrap.Tooltip = NgbsTooltip;

  function showModal(el) {
    var alreadyShown = el.classList.contains('show') && el._ngbsPhase === 'open';
    if (alreadyShown) {
      el._ngbsDesired = true;
      var bd0 = el.getAttribute('data-ngbs-backdrop') || 'true';
      if (bd0 !== 'false') backdropFor(el, 'modal');
      return;
    }
    if (el._ngbsPhase === 'opening') {
      el._ngbsDesired = true;
      if (!el.classList.contains('show')) {
        el._ngbsPhase = 'closed';
        showModal(el);
      }
      return;
    }
    document.querySelectorAll('[data-ngbs-kind="modal"]').forEach(function(other) {
      if (other === el) return;
      var otherOpen = other.classList.contains('show')
        || other._ngbsPhase === 'open'
        || other._ngbsPhase === 'opening'
        || other.getAttribute('data-ngbs-open') === 'true';
      if (!otherOpen) return;
      setOpenAttr(other, 'false');
      hideModal(other);
    });
    el._ngbsDesired = true;
    el._ngbsPhase = 'opening';
    portal(el);
    el._ngbsPrevFocus = document.activeElement;
    var bd = el.getAttribute('data-ngbs-backdrop') || 'true';
    if (bd !== 'false') backdropFor(el, 'modal');
    el.style.display = 'block';
    if (!el.classList.contains('show')) el.classList.add('show');
    el.setAttribute('aria-modal', 'true');
    el.removeAttribute('aria-hidden');
    lockBodyScroll(el);
    if (!el._ngbsKey) {
      el._ngbsKey = function(e) {
        if (e.key === 'Escape') {
          var kb = el.getAttribute('data-ngbs-keyboard');
          if (kb === 'false') return;
          e.preventDefault();
          setOpenAttr(el, 'false');
          dispatch(el, 'dismiss');
          hideModal(el);
        } else if (e.key === 'Tab') {
          var nodes = focusables(el);
          if (!nodes.length) { e.preventDefault(); el.focus(); return; }
          var first = nodes[0], last = nodes[nodes.length - 1];
          if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
          else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
      };
      document.addEventListener('keydown', el._ngbsKey, true);
    }
    if (el.getAttribute('data-ngbs-focus') !== 'false' && !el._ngbsFocusIn) {
      el._ngbsFocusIn = function(e) {
        if (el.getAttribute('data-ngbs-focus') === 'false') return;
        if (!el.classList.contains('show')) return;
        if (el.contains(e.target)) return;
        var pull = focusables(el)[0] || el.querySelector('.modal-dialog') || el;
        try { pull.focus(); } catch (err) {}
      };
      document.addEventListener('focusin', el._ngbsFocusIn, true);
    }
    if (!el._ngbsBackdropClick) {
      el._ngbsBackdropClick = function(e) {
        if (e.target !== el) return;
        var mode = el.getAttribute('data-ngbs-backdrop') || 'true';
        if (mode !== 'true') return;
        setOpenAttr(el, 'false');
        dispatch(el, 'dismiss');
        hideModal(el);
      };
      el.addEventListener('mousedown', el._ngbsBackdropClick);
    }
    if (el.getAttribute('data-ngbs-focus') !== 'false') {
      var focusFirst = focusables(el)[0] || el.querySelector('.modal-dialog') || el;
      try { focusFirst.focus(); } catch (err) {}
    }
    el._ngbsPhase = 'open';
    dispatch(el, 'shown');
    if (el.getAttribute('data-ngbs-open') !== 'true') hideModal(el);
  }

  function hideModal(el) {
    if (el._ngbsPhase === 'closed' || el._ngbsPhase === 'closing') {
      el._ngbsDesired = false;
      removeBackdrop(el);
      unlockBodyScroll(el);
      return;
    }
    el._ngbsDesired = false;
    el._ngbsPhase = 'closing';
    if (el.classList.contains('show')) el.classList.remove('show');
    el.style.display = 'none';
    el.setAttribute('aria-hidden', 'true');
    el.removeAttribute('aria-modal');
    removeBackdrop(el);
    if (el._ngbsKey) {
      document.removeEventListener('keydown', el._ngbsKey, true);
      el._ngbsKey = null;
    }
    if (el._ngbsFocusIn) {
      document.removeEventListener('focusin', el._ngbsFocusIn, true);
      el._ngbsFocusIn = null;
    }
    unlockBodyScroll(el);
    restoreFocus(el);
    el._ngbsPhase = 'closed';
    dispatch(el, 'hidden');
    if (el.getAttribute('data-ngbs-open') === 'true') showModal(el);
  }

  function showCollapse(el) {
    if (el.classList.contains('show')) return;
    if (!el.classList.contains('show')) el.classList.add('show');
    dispatch(el, 'shown');
    if (el.getAttribute('data-ngbs-open') !== 'true') hideCollapse(el);
  }
  function hideCollapse(el) {
    if (!el.classList.contains('show')) return;
    if (el.classList.contains('show')) el.classList.remove('show');
    dispatch(el, 'hidden');
    if (el.getAttribute('data-ngbs-open') === 'true') showCollapse(el);
  }

  function showOffcanvas(el) {
    if (el.classList.contains('show') && el._ngbsPhase === 'open') {
      el._ngbsDesired = true;
      return;
    }
    el._ngbsDesired = true;
    el._ngbsPhase = 'opening';
    el._ngbsPrevFocus = document.activeElement;
    portal(el);
    var bd = el.getAttribute('data-ngbs-backdrop') || 'true';
    if (bd !== 'false') {
      var b = backdropFor(el, 'offcanvas');
      if (!b._ngbsClick) {
        b._ngbsClick = function() {
          if ((el.getAttribute('data-ngbs-backdrop') || 'true') !== 'true') return;
          setOpenAttr(el, 'false');
          dispatch(el, 'dismiss');
          hideOffcanvas(el);
        };
        b.addEventListener('click', b._ngbsClick);
      }
    }
    if (!el.classList.contains('show')) el.classList.add('show');
    if (el.getAttribute('data-ngbs-scroll') !== 'true') lockBodyScroll(el);
    if (!el._ngbsKey) {
      el._ngbsKey = function(e) {
        if (e.key !== 'Escape') return;
        if (el.getAttribute('data-ngbs-keyboard') === 'false') return;
        setOpenAttr(el, 'false');
        dispatch(el, 'dismiss');
        hideOffcanvas(el);
      };
      document.addEventListener('keydown', el._ngbsKey, true);
    }
    el._ngbsPhase = 'open';
    dispatch(el, 'shown');
    if (el.getAttribute('data-ngbs-open') !== 'true') hideOffcanvas(el);
  }

  function hideOffcanvas(el) {
    if (el._ngbsPhase === 'closed') {
      el._ngbsDesired = false;
      removeBackdrop(el);
      el.style.removeProperty('visibility');
      unlockBodyScroll(el);
      restoreFocus(el);
      return;
    }
    el._ngbsDesired = false;
    if (el.classList.contains('show')) el.classList.remove('show');
    el.style.removeProperty('visibility');
    removeBackdrop(el);
    if (el._ngbsKey) {
      document.removeEventListener('keydown', el._ngbsKey, true);
      el._ngbsKey = null;
    }
    unlockBodyScroll(el);
    restoreFocus(el);
    el._ngbsPhase = 'closed';
    dispatch(el, 'hidden');
    if (el.getAttribute('data-ngbs-open') === 'true') showOffcanvas(el);
  }

  function menuOf(el) {
    return el.querySelector('.dropdown-menu') || el;
  }
  function toggleOf(el) {
    return el.querySelector('.dropdown-toggle, [data-ngbs-role="toggle"]') || el;
  }
  function dropdownItems(el) {
    var menu = menuOf(el);
    if (!menu || !menu.querySelectorAll) return [];
    return Array.prototype.filter.call(menu.querySelectorAll('.dropdown-item'), function(n) {
      if (n.classList.contains('disabled')) return false;
      if (n.getAttribute('disabled') != null) return false;
      if (n.getAttribute('aria-disabled') === 'true') return false;
      return true;
    });
  }

  function setOpenAttr(el, value) {
    if (el.getAttribute('data-ngbs-open') !== value) {
      el.setAttribute('data-ngbs-open', value);
    }
  }
  function showDropdown(el) {
    var menu = menuOf(el);
    var btn = toggleOf(el);
    if (menu.classList.contains('show')) {
      setOpenAttr(el, 'true');
      if (btn && btn.setAttribute) btn.setAttribute('aria-expanded', 'true');
      return;
    }
    menu.classList.add('show');
    setOpenAttr(el, 'true');
    if (btn && btn.setAttribute) btn.setAttribute('aria-expanded', 'true');
    dispatch(el, 'shown');
    dispatch(el, 'toggle');
  }
  function hideDropdown(el) {
    var menu = menuOf(el);
    var btn = toggleOf(el);
    if (!menu.classList.contains('show')) {
      setOpenAttr(el, 'false');
      if (btn && btn.setAttribute) btn.setAttribute('aria-expanded', 'false');
      return;
    }
    menu.classList.remove('show');
    setOpenAttr(el, 'false');
    if (btn && btn.setAttribute) btn.setAttribute('aria-expanded', 'false');
    dispatch(el, 'hidden');
    dispatch(el, 'toggle');
  }

  function initDropdown(el) {
    if (el._ngbsDropInited) return;
    el._ngbsDropInited = true;
    var btn = toggleOf(el);
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      if (btn.disabled || btn.getAttribute('disabled') != null || btn.classList.contains('disabled')) return;
      if (menuOf(el).classList.contains('show')) hideDropdown(el);
      else showDropdown(el);
    });
    el.addEventListener('click', function(e) {
      var item = e.target && e.target.closest ? e.target.closest('.dropdown-item') : null;
      if (!item || !el.contains(item)) return;
      if (item.classList.contains('disabled') || item.getAttribute('aria-disabled') === 'true') {
        e.preventDefault();
        return;
      }
      if (item.getAttribute('data-ngbs-item-toggle') === 'false') return;
      hideDropdown(el);
    });
    el.addEventListener('keydown', function(e) {
      var items = dropdownItems(el);
      var menu = menuOf(el);
      var shown = menu.classList.contains('show');
      var idx = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!shown) showDropdown(el);
        items = dropdownItems(el);
        if (!items.length) return;
        if (idx < 0) {
          if (e.key === 'ArrowDown') items[0].focus();
          else items[items.length - 1].focus();
          return;
        }
        if (e.key === 'ArrowDown') items[(idx + 1) % items.length].focus();
        else items[(idx - 1 + items.length) % items.length].focus();
        return;
      }
      if (e.key === 'Home') {
        if (!shown || !items.length) return;
        e.preventDefault();
        items[0].focus();
        return;
      }
      if (e.key === 'End') {
        if (!shown || !items.length) return;
        e.preventDefault();
        items[items.length - 1].focus();
        return;
      }
      if (e.key === 'Escape') {
        if (!shown) return;
        e.preventDefault();
        hideDropdown(el);
        if (btn && btn.focus) btn.focus();
        return;
      }
      if (e.key === 'Tab' && shown) {
        hideDropdown(el);
      }
    });
    if (!window.__ngbsDropDoc) {
      window.__ngbsDropDoc = true;
      document.addEventListener('click', function(e) {
        document.querySelectorAll('[data-ngbs-kind="dropdown"]').forEach(function(d) {
          if (!d.contains(e.target)) hideDropdown(d);
        });
      });
      document.addEventListener('keydown', function(e) {
        if (e.key !== 'Escape') return;
        document.querySelectorAll('[data-ngbs-kind="dropdown"]').forEach(hideDropdown);
      });
    }
  }

  function resolveTarget(el) {
    var spec = el.getAttribute('data-ngbs-target') || '';
    var kind = el.getAttribute('data-ngbs-target-kind') || 'public';
    if (!spec) return null;
    if (kind === 'eid') {
      var n = document.getElementById('c' + spec) || document.querySelector('[data-ngbs-eid="' + spec + '"]');
      return n;
    }
    return document.querySelector('[data-ngbs-public-id="' + spec + '"]')
      || document.getElementById(spec)
      || document.querySelector('[id="' + spec + '"]');
  }

  function placeTooltip(tip, target, placement) {
    var r = target.getBoundingClientRect();
    var t = tip.getBoundingClientRect();
    var p = !placement || placement === 'auto' ? 'top' : placement;
    var top, left;
    if (p.indexOf('bottom') === 0) { top = r.bottom + 8; left = r.left + (r.width - t.width) / 2; }
    else if (p.indexOf('left') === 0) { top = r.top + (r.height - t.height) / 2; left = r.left - t.width - 8; }
    else if (p.indexOf('right') === 0) { top = r.top + (r.height - t.height) / 2; left = r.right + 8; }
    else { top = r.top - t.height - 8; left = r.left + (r.width - t.width) / 2; }
    tip.style.position = 'fixed';
    tip.style.top = Math.max(0, top) + 'px';
    tip.style.left = Math.max(0, left) + 'px';
  }

  function tooltipDelay(el, phase) {
    var raw = el.getAttribute('data-ngbs-delay');
    if (!raw) return 0;
    var parsed;
    try { parsed = JSON.parse(raw); } catch (err) { parsed = Number(raw); }
    if (typeof parsed === 'number') return Number.isFinite(parsed) ? Math.max(0, parsed) : 0;
    if (parsed && typeof parsed === 'object') {
      var value = Number(parsed[phase]);
      return Number.isFinite(value) ? Math.max(0, value) : 0;
    }
    return 0;
  }

  function initTooltip(el) {
    if (el._ngbsTipInited) return;
    el._ngbsTipInited = true;
    el.style.display = 'none';
    var target = resolveTarget(el);
    if (!target) {
      el._ngbsTargetWatch = new MutationObserver(function() {
        if (!document.contains(el)) {
          el._ngbsTargetWatch.disconnect();
          el._ngbsTargetWatch = null;
          return;
        }
        var resolved = resolveTarget(el);
        if (!resolved) return;
        el._ngbsTargetWatch.disconnect();
        el._ngbsTargetWatch = null;
        el._ngbsTipInited = false;
        initTooltip(el);
        if (el._ngbsInited) sync(el);
      });
      el._ngbsTargetWatch.observe(document.body, { childList: true, subtree: true, attributes: true });
      return;
    }
    var tip = document.createElement('div');
    tip.className = 'tooltip bs-tooltip-auto';
    tip.setAttribute('role', 'tooltip');
    var arrow = document.createElement('div');
    arrow.className = 'tooltip-arrow';
    var inner = document.createElement('div');
    inner.className = 'tooltip-inner';
    while (el.firstChild) inner.appendChild(el.firstChild);
    tip.appendChild(arrow);
    tip.appendChild(inner);
    tip.style.display = 'none';
    overlayRoot().appendChild(tip);
    el._ngbsTip = tip;
    el._ngbsTipTarget = target;
    target._ngbsTipEl = tip;
    el._ngbsTipHandlers = [];
    el._ngbsTipShowTimer = null;
    el._ngbsTipHideTimer = null;
    var trigger = (el.getAttribute('data-ngbs-trigger') || 'hover focus').split(/\s+/);

    function bind(node, event, handler) {
      node.addEventListener(event, handler);
      el._ngbsTipHandlers.push({ node: node, event: event, handler: handler });
    }

    function showNow() {
      if (!document.contains(target)) { disposeEl(el); return; }
      if (tip.classList.contains('show')) return;
      if (el._ngbsTipHideTimer) {
        clearTimeout(el._ngbsTipHideTimer);
        el._ngbsTipHideTimer = null;
      }
      tip.style.display = 'block';
      tip.classList.add('show');
      placeTooltip(tip, target, el.getAttribute('data-ngbs-placement') || 'auto');
    }

    function show() {
      if (tip.classList.contains('show')) return;
      if (el._ngbsTipShowTimer) clearTimeout(el._ngbsTipShowTimer);
      var delay = tooltipDelay(el, 'show');
      if (delay > 0) {
        el._ngbsTipShowTimer = setTimeout(function() {
          el._ngbsTipShowTimer = null;
          showNow();
        }, delay);
      }
      else showNow();
    }

    function hideNow() {
      tip.classList.remove('show');
      tip.style.display = 'none';
    }

    function hide() {
      if (el._ngbsTipShowTimer) {
        clearTimeout(el._ngbsTipShowTimer);
        el._ngbsTipShowTimer = null;
      }
      if (el._ngbsTipHideTimer) clearTimeout(el._ngbsTipHideTimer);
      var delay = tooltipDelay(el, 'hide');
      if (delay > 0) {
        el._ngbsTipHideTimer = setTimeout(function() {
          el._ngbsTipHideTimer = null;
          hideNow();
        }, delay);
      }
      else hideNow();
    }

    function toggle() {
      if (tip.classList.contains('show')) hide(); else show();
    }
    if (trigger.indexOf('hover') >= 0 || trigger.indexOf('mouseover') >= 0) {
      bind(target, 'mouseenter', show);
      bind(target, 'mouseleave', hide);
    }
    if (trigger.indexOf('focus') >= 0) {
      bind(target, 'focus', show);
      bind(target, 'blur', hide);
    }
    if (trigger.indexOf('click') >= 0) {
      bind(target, 'click', toggle);
    }
    if (el.getAttribute('data-ngbs-autohide') === 'false') {
      bind(tip, 'mouseenter', function() {
        if (el._ngbsTipHideTimer) {
          clearTimeout(el._ngbsTipHideTimer);
          el._ngbsTipHideTimer = null;
        }
      });
      bind(tip, 'mouseleave', hide);
    }
    el._ngbsTargetWatch = new MutationObserver(function() {
      if (!document.contains(target)) disposeEl(el);
    });
    el._ngbsTargetWatch.observe(document.body, { childList: true, subtree: true });
    if (window.bootstrap && window.bootstrap.Tooltip && window.bootstrap.Tooltip !== NgbsTooltip) {
      try {
        el._bsTooltip = window.bootstrap.Tooltip.getOrCreateInstance(target, {
          title: function() { return inner; },
          html: true,
          container: overlayRoot(),
          placement: el.getAttribute('data-ngbs-placement') || 'auto',
          trigger: el.getAttribute('data-ngbs-trigger') || 'hover focus',
          delay: (function() {
            var raw = el.getAttribute('data-ngbs-delay');
            if (!raw) return 0;
            try { return JSON.parse(raw); } catch (err) { return Number(raw) || 0; };
          })(),
          sanitize: false
        });
      } catch (err) {}
    }
  }

  function showTooltip(el) {
    if (!el._ngbsTip) return;
    if (el._ngbsTip.classList.contains('show')) return;
    var target = el._ngbsTipTarget;
    if (!target || !document.contains(target)) { disposeEl(el); return; }
    if (el._ngbsTipShowTimer) clearTimeout(el._ngbsTipShowTimer);
    var delay = tooltipDelay(el, 'show');
    if (delay > 0) {
      el._ngbsTipShowTimer = setTimeout(function() {
        el._ngbsTipShowTimer = null;
        el._ngbsTip.style.display = 'block';
        el._ngbsTip.classList.add('show');
        placeTooltip(el._ngbsTip, target, el.getAttribute('data-ngbs-placement') || 'auto');
      }, delay);
    } else {
      el._ngbsTip.style.display = 'block';
      el._ngbsTip.classList.add('show');
      placeTooltip(el._ngbsTip, target, el.getAttribute('data-ngbs-placement') || 'auto');
    }
  }

  function hideTooltip(el) {
    if (el._ngbsTipShowTimer) {
      clearTimeout(el._ngbsTipShowTimer);
      el._ngbsTipShowTimer = null;
    }
    if (el._ngbsTipHideTimer) {
      clearTimeout(el._ngbsTipHideTimer);
      el._ngbsTipHideTimer = null;
    }
    if (el._ngbsTip) {
      el._ngbsTip.classList.remove('show');
      el._ngbsTip.style.display = 'none';
    }
  }

  function armToastTimer(el) {
    var dur = el.getAttribute('data-ngbs-duration');
    if (!dur || Number(dur) <= 0 || el._ngbsTimer) return;
    el._ngbsTimer = setTimeout(function() {
      el._ngbsTimer = null;
      setOpenAttr(el, 'false');
      hideToast(el);
    }, Number(dur));
  }

  function showToast(el) {
    if (el.classList.contains('show')) {
      armToastTimer(el);
      return;
    }
    portal(el);
    el.classList.add('show');
    el.style.display = 'block';
    armToastTimer(el);
    dispatch(el, 'shown');
  }
  function hideToast(el) {
    if (!el.classList.contains('show')) return;
    if (el._ngbsTimer) { clearTimeout(el._ngbsTimer); el._ngbsTimer = null; }
    el.classList.remove('show');
    el.style.display = 'none';
    dispatch(el, 'hidden');
  }

  function initToast(el) {
    if (el._ngbsToastInited) return;
    el._ngbsToastInited = true;
    el.addEventListener('click', function(e) {
      var t = e.target;
      if (t && t.getAttribute && t.getAttribute('data-ngbs-dismiss') === 'toast') {
        el.setAttribute('data-ngbs-open', 'false');
        dispatch(el, 'dismiss');
        hideToast(el);
      }
    });
  }

  function initOne(el) {
    if (!el || !el.getAttribute) return;
    var kind = el.getAttribute('data-ngbs-kind');
    if (!kind) return;
    if (kind === 'dropdown') initDropdown(el);
    if (kind === 'tooltip') initTooltip(el);
    if (kind === 'toast') initToast(el);
    if (kind === 'modal') {
      el.addEventListener('click', function(e) {
        var t = e.target;
        if (t && t.getAttribute && t.getAttribute('data-ngbs-dismiss') === 'modal') {
          setOpenAttr(el, 'false');
          dispatch(el, 'dismiss');
          hideModal(el);
        }
      });
    }
    if (kind === 'offcanvas') {
      el.addEventListener('click', function(e) {
        var t = e.target;
        if (t && t.getAttribute && t.getAttribute('data-ngbs-dismiss') === 'offcanvas') {
          setOpenAttr(el, 'false');
          dispatch(el, 'dismiss');
          hideOffcanvas(el);
        }
      });
    }
    el._ngbsInited = true;
    sync(el);
  }

  function sync(el) {
    if (!el || !el.getAttribute) return;
    var kind = el.getAttribute('data-ngbs-kind');
    if (!kind) return;
    if (!el._ngbsInited) { initOne(el); return; }
    var want = el.getAttribute('data-ngbs-open') === 'true';
    if (kind === 'modal') {
      if (window.bootstrap && window.bootstrap.Modal && window.bootstrap.Modal.getOrCreateInstance) {
        try {
          var inst = window.bootstrap.Modal.getOrCreateInstance(el, {
            backdrop: (function() {
              var v = el.getAttribute('data-ngbs-backdrop') || 'true';
              if (v === 'static') return 'static';
              return v !== 'false';
            })(),
            keyboard: el.getAttribute('data-ngbs-keyboard') !== 'false',
            focus: el.getAttribute('data-ngbs-focus') !== 'false'
          });
          if (inst && inst !== el._ngbsModal && inst.show && inst.hide) {
            portal(el);
            if (want) inst.show(); else inst.hide();
            return;
          }
        } catch (err) {}
      }
      if (want) showModal(el); else hideModal(el);
      // Definitive convergence: DOM truth wins over the phase machine.
      var shownNow = el.classList.contains('show');
      if (want && shownNow) {
        var bdWanted = (el.getAttribute('data-ngbs-backdrop') || 'true') !== 'false';
        if (bdWanted) backdropFor(el, 'modal');
      }
      if (!want && !shownNow) {
        removeBackdrop(el);
      }
    } else if (kind === 'collapse') {
      if (want) showCollapse(el); else hideCollapse(el);
    } else if (kind === 'offcanvas') {
      if (want) showOffcanvas(el); else hideOffcanvas(el);
    } else if (kind === 'dropdown') {
      if (want) showDropdown(el); else hideDropdown(el);
    } else if (kind === 'toast') {
      if (want) showToast(el); else hideToast(el);
    } else if (kind === 'tooltip') {
      if (!el._ngbsTipInited) initTooltip(el);
      if (want) showTooltip(el); else hideTooltip(el);
    }
  }

  function disposeEl(el) {
    if (!el || !el.getAttribute) return;
    var kind = el.getAttribute('data-ngbs-kind');
    if (!kind) return;
    if (el._ngbsTimer) { clearTimeout(el._ngbsTimer); el._ngbsTimer = null; }
    if (el._ngbsKey) {
      document.removeEventListener('keydown', el._ngbsKey, true);
      el._ngbsKey = null;
    }
    if (el._ngbsFocusIn) {
      document.removeEventListener('focusin', el._ngbsFocusIn, true);
      el._ngbsFocusIn = null;
    }
    if (el._ngbsTipShowTimer) {
      clearTimeout(el._ngbsTipShowTimer);
      el._ngbsTipShowTimer = null;
    }
    if (el._ngbsTipHideTimer) {
      clearTimeout(el._ngbsTipHideTimer);
      el._ngbsTipHideTimer = null;
    }
    if (el._ngbsTipHandlers) {
      el._ngbsTipHandlers.forEach(function(binding) {
        binding.node.removeEventListener(binding.event, binding.handler);
      });
      el._ngbsTipHandlers = [];
    }
    if (el._ngbsTip && el._ngbsTip.remove) el._ngbsTip.remove();
    if (el._ngbsTargetWatch) {
      el._ngbsTargetWatch.disconnect();
      el._ngbsTargetWatch = null;
    }
    if (el._ngbsTipTarget && el._ngbsTipTarget._ngbsTipEl === el._ngbsTip) {
      el._ngbsTipTarget._ngbsTipEl = null;
    }
    if (el._bsTooltip && el._bsTooltip.dispose) {
      try { el._bsTooltip.dispose(); } catch (err) {}
    }
    removeBackdrop(el);
    unlockBodyScroll(el);
    restoreFocus(el);
    el._ngbsPhase = 'closed';
  }
  window.ngbsDispose = disposeEl;
  window.ngbsSync = sync;

  function scan(root) {
    if (!root) return;
    var list = [];
    if (root.getAttribute && root.getAttribute('data-ngbs-kind')) list.push(root);
    if (root.querySelectorAll) {
      root.querySelectorAll('[data-ngbs-kind]').forEach(function(n) { list.push(n); });
    }
    list.forEach(function(n) {
      if (!n._ngbsInited) initOne(n);
      else sync(n);
    });
  }

  var mo = new MutationObserver(function(mutations) {
    for (var i = 0; i < mutations.length; i++) {
      var m = mutations[i];
      if (m.type === 'attributes' && m.target && m.target.getAttribute) {
        if (m.target.getAttribute('data-ngbs-kind')) sync(m.target);
      }
      if (m.type === 'childList') {
        m.addedNodes.forEach(function(n) {
          if (n.nodeType === 1) scan(n);
        });
        m.removedNodes.forEach(function(n) {
          if (n.nodeType !== 1) return;
          if (document.contains(n)) return;
          disposeEl(n);
          if (n.querySelectorAll) {
            n.querySelectorAll('[data-ngbs-kind]').forEach(disposeEl);
          }
        });
      }
    }
  });

  function start() {
    overlayRoot();
    mo.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['data-ngbs-open', 'data-ngbs-kind', 'data-ngbs-epoch']
    });
    scan(document);
  }
  if (document.body) start();
  else document.addEventListener('DOMContentLoaded', start);
})();
"""


def _make_surfaces(impl_cls: type) -> tuple[type, type]:
    name = getattr(impl_cls, "component_name", None) or impl_cls.__name__
    if name.startswith("_"):
        name = name[1:]
    if name.endswith("Impl"):
        name = name[:-4]
    return make_surface_classes(impl_cls, component_name=name)


def _surface_of(el: Any, explicit: str | None) -> str:
    if explicit in {"native", "compat"}:
        return explicit
    value = getattr(el, "_surface", None) or getattr(type(el), "_surface", None)
    return value if value in {"native", "compat"} else "native"


def _flatten_children(children: Any) -> list[Any]:
    if children is None:
        return []
    if isinstance(children, (str, int, float)):
        return [children]
    element_type: Any
    try:
        from nicegui.element import Element as element_type
    except Exception:  # pragma: no cover
        element_type = ui.element
    if isinstance(children, element_type):
        return [children]
    if isinstance(children, (list, tuple)):
        out: list[Any] = []
        for child in children:
            out.extend(_flatten_children(child))
        return out
    raise TypeError(f"Unsupported child type: {type(children)!r}")


def _adopt_into(host: Any, children: Any, *, owner: Any = None) -> None:
    seen: set[int] = set()
    for child in _flatten_children(children):
        if child is None:
            continue
        if isinstance(child, (str, int, float)):
            with host:
                span = ui.element("span").classes("ngbs-text")
                if hasattr(span, "set_text"):
                    span.set_text(str(child))
                else:
                    set_element_text(span, str(child))
        elif isinstance(child, ui.element):
            ident = id(child)
            if ident in seen:
                raise ChildrenError("Duplicate ownership")
            seen.add(ident)
            BootstrapElementMixin._validate_adoptee(owner if owner is not None else host, child)
            child.move(host)
        else:
            raise TypeError(f"Unsupported child type: {type(child)!r}")


def _fill_text_or_children(host: Any, children: Any, *, owner: Any = None) -> None:
    if children is None:
        return
    if isinstance(children, (str, int, float)) and not isinstance(children, bool):
        text = str(children)
        if hasattr(host, "set_text"):
            host.set_text(text)
        else:
            set_element_text(host, text)
        return
    _adopt_into(host, children, owner=owner)


def _slot_children(host: Any) -> list[Any]:
    slot = getattr(host, "default_slot", None)
    if slot is not None:
        return list(getattr(slot, "children", []) or [])
    slots = getattr(host, "slots", None)
    if isinstance(slots, dict):
        default = slots.get("default")
        if default is not None:
            return list(getattr(default, "children", []) or [])
    return []


def _collect_accordion_items(host: Any) -> list[Any]:
    items: list[Any] = []
    for child in _slot_children(host):
        if getattr(child, "component_name", None) == "AccordionItem":
            items.append(child)
    return items


def _find_ancestor(el: Any, component_name: str) -> Any | None:
    seen: set[int] = set()
    current = el
    while current is not None:
        ident = id(current)
        if ident in seen:
            break
        seen.add(ident)
        slot = getattr(current, "parent_slot", None)
        parent = (
            getattr(slot, "parent", None) if slot is not None else getattr(current, "parent", None)
        )
        if parent is None:
            break
        if getattr(parent, "component_name", None) == component_name:
            return parent
        current = parent
    return None


def _style_obj(target: Any, style: dict[str, Any] | None) -> str:
    if not style:
        return ""
    unitless = {
        "opacity",
        "z-index",
        "zIndex",
        "font-weight",
        "fontWeight",
        "line-height",
        "lineHeight",
        "flex",
        "flex-grow",
        "flexGrow",
        "flex-shrink",
        "flexShrink",
        "order",
        "zoom",
        "animation-iteration-count",
        "animationIterationCount",
    }
    parts: list[str] = []
    for key, value in style.items():
        css_key = key
        if isinstance(value, (int, float)) and key not in unitless:
            value = f"{value}px"
        parts.append(f"{css_key}: {value}")
    if parts:
        css = "; ".join(parts)
        if target is not None:
            target.style(css)
        return css
    return ""


def _ensure_overlay_runtime() -> None:
    global _RUNTIME_READY
    if _RUNTIME_READY:
        return
    ui.add_head_html(f"<style>@layer overrides {{\n{_OVERLAY_CSS}\n}}</style>", shared=True)
    ui.add_head_html(f"<script>{_OVERLAY_JS}</script>", shared=True)
    _RUNTIME_READY = True


def _bind_kind(el: Any, kind: str, **attrs: Any) -> None:
    el._props["data-ngbs-kind"] = kind
    with contextlib.suppress(Exception):
        el._props["data-ngbs-eid"] = str(el.id)
    for key, value in attrs.items():
        if value is None:
            continue
        attr = key if key.startswith("data-") else f"data-ngbs-{key.replace('_', '-')}"
        el._props[attr] = ("true" if value else "false") if isinstance(value, bool) else str(value)


def _portal_to_overlay_root(el: Any) -> None:
    root = None
    with contextlib.suppress(Exception):
        root = ensure_overlay_root()
    if root is not None and root is not el and hasattr(el, "move"):
        with contextlib.suppress(Exception):
            el.move(root)
            return
    el._props["data-ngbs-portal"] = "true"


def _set_open_state_props(el: Any, value: bool) -> None:
    el._is_open = bool(value)
    props: dict[str, Any] = getattr(el, "_props", {})
    props["data-ngbs-open"] = "true" if el._is_open else "false"
    epoch = int(getattr(el, "_ngbs_epoch", 0)) + 1
    el._ngbs_epoch = epoch
    props["data-ngbs-epoch"] = str(epoch)


def _sync_open_class(el: Any) -> None:
    classes = getattr(el, "classes", None)
    if not getattr(el, "_css_show", False) or not callable(classes):
        return
    if getattr(el, "_is_open", False):
        classes(add="show")
    else:
        classes(remove="show")


def _echo_open_state(el: Any, value: bool) -> None:
    desired = "true" if value else "false"
    props = getattr(el, "_props", {})
    if props.get("data-ngbs-open") != desired or bool(getattr(el, "_is_open", False)) != value:
        _set_open_state_props(el, value)
    _sync_open_class(el)


class _SlotRedirect:
    def __enter__(self) -> Any:
        if getattr(self, "_children_passed", False):
            raise ChildrenError("Cannot pass children= and use as a context manager")
        host = getattr(self, "_slot_host", None)
        if host is not None:
            host.__enter__()
            return self
        parent_enter = getattr(super(), "__enter__", None)
        if parent_enter is not None:
            return parent_enter()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> Any:
        host = getattr(self, "_slot_host", None)
        if host is not None:
            return host.__exit__(exc_type, exc, tb)
        parent_exit = getattr(super(), "__exit__", None)
        if parent_exit is not None:
            return parent_exit(exc_type, exc, tb)
        return None


class _OpenMixin:
    _css_show: bool = True

    @property
    def is_open(self) -> bool:
        return bool(getattr(self, "_is_open", False))

    @is_open.setter
    def is_open(self, value: bool) -> None:
        self._apply_open(bool(value))

    def _apply_open(self, value: bool) -> None:
        _set_open_state_props(self, value)
        _sync_open_class(self)
        update = getattr(self, "update", None)
        if callable(update):
            update()

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def toggle(self) -> None:
        self.is_open = not self.is_open

    def show(self) -> None:
        self.open()

    def hide(self) -> None:
        self.close()


def _wire_overlay_events(
    el: Any,
    *,
    on_show: Callable[..., Any] | None = None,
    on_shown: Callable[..., Any] | None = None,
    on_hide: Callable[..., Any] | None = None,
    on_hidden: Callable[..., Any] | None = None,
    on_dismiss: Callable[..., Any] | None = None,
) -> None:
    el._on_show_cb = on_show
    el._on_shown_cb = on_shown
    el._on_hide_cb = on_hide
    el._on_hidden_cb = on_hidden
    el._on_dismiss_cb = on_dismiss

    def _shown(_e: Any = None) -> None:
        _echo_open_state(el, True)
        if el._on_shown_cb is not None:
            el._on_shown_cb()

    def _hidden(_e: Any = None) -> None:
        _echo_open_state(el, False)
        if el._on_hidden_cb is not None:
            el._on_hidden_cb()

    def _dismiss(_e: Any = None) -> None:
        _echo_open_state(el, False)
        if el._on_dismiss_cb is not None:
            el._on_dismiss_cb()

    el.on("shown", _shown)
    el.on("hidden", _hidden)
    el.on("dismiss", _dismiss)
    if on_show is not None:
        el.on("show", lambda _e=None: on_show())
    if on_hide is not None:
        el.on("hide", lambda _e=None: on_hide())


class _ModalImpl(_SlotRedirect, _OpenMixin, BootstrapElement):
    component_name = "Modal"
    styling_target = "root"
    reserved_classes = ("modal", "fade", "show")
    _css_show = True

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        is_open: bool = False,
        size: str | None = None,
        fullscreen: bool | str = False,
        backdrop: bool | str = True,
        centered: bool = False,
        scrollable: bool = False,
        fade: bool = True,
        keyboard: bool = True,
        enforceFocus: bool | None = None,
        enforce_focus: bool | None = None,
        labelledby: str | None = None,
        dialog_class_name: str | None = None,
        dialog_style: dict[str, Any] | None = None,
        content_class_name: str | None = None,
        content_style: dict[str, Any] | None = None,
        backdrop_class_name: str | None = None,
        backdrop_style: dict[str, Any] | None = None,
        class_name: str | None = None,
        dialogStyle: dict[str, Any] | None = None,
        contentStyle: dict[str, Any] | None = None,
        on_show: Callable[..., Any] | None = None,
        on_shown: Callable[..., Any] | None = None,
        on_hide: Callable[..., Any] | None = None,
        on_hidden: Callable[..., Any] | None = None,
        on_dismiss: Callable[..., Any] | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        className: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        if dialog_style is None:
            dialog_style = dialogStyle
        if content_style is None:
            content_style = contentStyle
        if enforce_focus is None and enforceFocus is not None:
            enforce_focus = enforceFocus
        elif (
            enforce_focus is not None
            and enforceFocus is not None
            and bool(enforce_focus) != bool(enforceFocus)
        ):
            raise PropConflictError("enforce_focus/enforceFocus conflict")
        if enforce_focus is None:
            enforce_focus = True
        _ensure_overlay_runtime()
        super().__init__(
            children=None,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes("modal")
        if fade:
            self.classes("fade")
        self._props["tabindex"] = "-1"
        self._props["role"] = "dialog"
        if labelledby:
            self._props["aria-labelledby"] = labelledby
        dialog_classes = modal_dialog_classes(
            size=size,
            centered=centered,
            scrollable=scrollable,
            fullscreen=fullscreen,
            dialog_class_name=dialog_class_name,
        )
        with self:
            self._dialog = ui.element("div").classes(" ".join(dialog_classes))
            _style_obj(self._dialog, dialog_style)
            with self._dialog:
                content_classes = ["modal-content"]
                if content_class_name:
                    content_classes.append(content_class_name)
                self._content = ui.element("div").classes(" ".join(content_classes))
                _style_obj(self._content, content_style)
        self._slot_host = self._content
        self._children_passed = children is not None
        if children is not None:
            _adopt_into(self._content, children, owner=self)
        self._apply_open(bool(is_open))
        backdrop_attr = backdrop if isinstance(backdrop, str) else bool(backdrop)
        _bind_kind(
            self,
            "modal",
            open=bool(is_open),
            backdrop=backdrop_attr,
            keyboard=bool(keyboard),
            focus=bool(enforce_focus),
        )
        if backdrop_class_name:
            self._props["data-ngbs-backdrop-class"] = backdrop_class_name
        if backdrop_style:
            self._props["data-ngbs-backdrop-style"] = _style_obj(None, backdrop_style)
        _portal_to_overlay_root(self)
        _wire_overlay_events(
            self,
            on_show=on_show,
            on_shown=on_shown,
            on_hide=on_hide,
            on_hidden=on_hidden,
            on_dismiss=on_dismiss,
        )

    def _handle_delete(self) -> None:  # noqa: D401
        self._props["data-ngbs-open"] = "false"
        super()._handle_delete()


class _ModalHeaderImpl(_SlotRedirect, BootstrapElement):
    component_name = "ModalHeader"
    styling_target = "root"
    reserved_classes = ("modal-header",)

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        close_button: bool = True,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        super().__init__(
            children=None,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes("modal-header")
        with self:
            self._slot_host = ui.element("div")
            if close_button:
                close = ui.element("button").classes("btn-close")
                close._props["type"] = "button"
                close._props["data-ngbs-dismiss"] = "modal"
                close._props["aria-label"] = "Close"
        self._children_passed = children is not None
        if children is not None:
            _fill_text_or_children(self._slot_host, children, owner=self)


class _ModalTitleImpl(BootstrapElement):
    component_name = "ModalTitle"
    styling_target = "root"
    reserved_classes = ("modal-title",)

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        tag: str = "h5",
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        super().__init__(
            children=children,
            tag=tag,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes("modal-title")
        if not id:
            self._props["id"] = f"ngbs-modal-title-{self.id}"


class _ModalBodyImpl(BootstrapElement):
    component_name = "ModalBody"
    styling_target = "root"
    reserved_classes = ("modal-body",)

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        super().__init__(
            children=children,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes("modal-body")


class _ModalFooterImpl(BootstrapElement):
    component_name = "ModalFooter"
    styling_target = "root"
    reserved_classes = ("modal-footer",)

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        super().__init__(
            children=children,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes("modal-footer")


class _CollapseImpl(_OpenMixin, BootstrapElement):
    """Collapse panel with height or width disclosure."""

    component_name = "Collapse"
    styling_target = "root"
    reserved_classes = ("collapse", "show", "navbar-collapse", "collapse-horizontal")
    _css_show = True

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        is_open: bool = False,
        navbar: bool = False,
        dimension: str = "height",
        on_show: Callable[..., Any] | None = None,
        on_shown: Callable[..., Any] | None = None,
        on_hide: Callable[..., Any] | None = None,
        on_hidden: Callable[..., Any] | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        struct = collapse_structural_classes(navbar=navbar, dimension=dimension)
        if surface == "compat" and dimension != "height":
            raise UnsupportedPropError("dimension")
        _ensure_overlay_runtime()
        super().__init__(
            children=children,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes(" ".join(struct))
        self._apply_open(bool(is_open))
        _bind_kind(self, "collapse", open=bool(is_open), dimension=dimension)
        _wire_overlay_events(
            self, on_show=on_show, on_shown=on_shown, on_hide=on_hide, on_hidden=on_hidden
        )


class _FadeImpl(BootstrapElement):
    """Fade transition wrapper using ``is_in`` (not ``is_open``)."""

    component_name = "Fade"
    styling_target = "root"
    reserved_classes = ("fade", "show")

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        is_in: bool = False,
        timeout: int | dict[str, Any] | None = None,
        appear: bool = False,
        enter: bool = True,
        exit: bool = True,
        unmount_on_exit: bool = False,
        is_open: Any = _UNSET,
        tag: str = "div",
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        if is_open is not _UNSET:
            raise UnsupportedPropError("is_open")
        super().__init__(
            children=children,
            tag=tag,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes("fade")
        self._timeout = timeout
        self._appear = bool(appear)
        self._enter = bool(enter)
        self._exit = bool(exit)
        self._unmount_on_exit = bool(unmount_on_exit)
        self._is_in = False
        self._apply_in(bool(is_in), initial=True)

    def _apply_in(self, value: bool, *, initial: bool = False) -> None:
        self._is_in = bool(value)
        if self._is_in:
            self.classes(add="show")
            if self._unmount_on_exit:
                self._props.pop("hidden", None)
        else:
            self.classes(remove="show")
            if self._unmount_on_exit:
                self._props["hidden"] = True
        if not initial:
            update = getattr(self, "update", None)
            if callable(update):
                update()

    @property
    def is_in(self) -> bool:
        return bool(self._is_in)

    @is_in.setter
    def is_in(self, value: bool) -> None:
        self._apply_in(bool(value))

    def show(self) -> None:
        self.is_in = True

    def hide(self) -> None:
        self.is_in = False


class _OffcanvasImpl(_SlotRedirect, _OpenMixin, BootstrapElement):
    component_name = "Offcanvas"
    styling_target = "root"
    reserved_classes = (
        "offcanvas",
        "offcanvas-start",
        "offcanvas-end",
        "offcanvas-top",
        "offcanvas-bottom",
        "show",
    )
    _css_show = True

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        is_open: bool = False,
        placement: str = "start",
        backdrop: bool | str = True,
        scroll: bool = False,
        keyboard: bool = True,
        title: str | None = None,
        labelledby: str | None = None,
        header_class_name: str | None = None,
        body_class_name: str | None = None,
        on_show: Callable[..., Any] | None = None,
        on_shown: Callable[..., Any] | None = None,
        on_hide: Callable[..., Any] | None = None,
        on_hidden: Callable[..., Any] | None = None,
        on_dismiss: Callable[..., Any] | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        struct = offcanvas_structural_classes(placement=placement)
        _ensure_overlay_runtime()
        super().__init__(
            children=None,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes(" ".join(struct))
        self._props["tabindex"] = "-1"
        with self:
            if title is not None:
                header_classes = ["offcanvas-header"]
                if header_class_name:
                    header_classes.append(header_class_name)
                header = ui.element("div").classes(" ".join(header_classes))
                with header:
                    heading = ui.element("h5").classes("offcanvas-title")
                    title_dom_id = labelledby or f"ngbs-offcanvas-title-{self.id}"
                    heading._props["id"] = title_dom_id
                    if hasattr(heading, "set_text"):
                        heading.set_text(str(title))
                    else:
                        set_element_text(heading, str(title))
                    close = ui.element("button").classes("btn-close")
                    close._props["type"] = "button"
                    close._props["data-ngbs-dismiss"] = "offcanvas"
                    close._props["aria-label"] = "Close"
                    self._props["aria-labelledby"] = title_dom_id
            elif labelledby:
                self._props["aria-labelledby"] = labelledby
            body_classes = ["offcanvas-body"]
            if body_class_name:
                body_classes.append(body_class_name)
            self._slot_host = ui.element("div").classes(" ".join(body_classes))
        self._children_passed = children is not None
        if children is not None:
            _adopt_into(self._slot_host, children, owner=self)
        self._apply_open(bool(is_open))
        backdrop_attr = backdrop if isinstance(backdrop, str) else bool(backdrop)
        _bind_kind(
            self,
            "offcanvas",
            open=bool(is_open),
            backdrop=backdrop_attr,
            keyboard=bool(keyboard),
            scroll=bool(scroll),
            placement=placement,
        )
        _portal_to_overlay_root(self)
        _wire_overlay_events(
            self,
            on_show=on_show,
            on_shown=on_shown,
            on_hide=on_hide,
            on_hidden=on_hidden,
            on_dismiss=on_dismiss,
        )

    def _handle_delete(self) -> None:
        self._props["data-ngbs-open"] = "false"
        super()._handle_delete()


class _DropdownMenuImpl(_SlotRedirect, _OpenMixin, BootstrapElement):
    component_name = "DropdownMenu"
    styling_target = "root"
    reserved_classes = ("dropdown", "dropup", "dropstart", "dropend", "btn-group", "nav-item")
    _css_show = False

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        label: str | None = None,
        color: str = "secondary",
        size: str | None = None,
        direction: str = "down",
        menu_variant: str | None = None,
        align_end: bool | None = None,
        disabled: bool = False,
        nav: bool = False,
        caret: bool = True,
        in_navbar: bool = False,
        group: bool = False,
        toggle_style: dict[str, Any] | None = None,
        toggle_class_name: str | None = None,
        on_item_click: Any = _UNSET,
        is_open: Any = _UNSET,
        on_toggle: Callable[..., Any] | None = None,
        right: Any = _UNSET,
        addon_type: Any = _UNSET,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        if right is not _UNSET:
            raise UnsupportedPropError("right")
        if addon_type is not _UNSET:
            raise UnsupportedPropError("addon_type")
        if surface == "compat" and is_open is not _UNSET:
            raise UnsupportedPropError("is_open is a native-only extension on DropdownMenu")
        if surface == "compat" and on_item_click is not _UNSET:
            raise UnsupportedPropError("on_item_click is a native-only extension on DropdownMenu")
        nav_like = bool(nav or in_navbar)
        root_classes = dropdown_root_classes(
            direction=direction, nav=nav, group=group, in_navbar=in_navbar
        )
        toggle_classes = dropdown_toggle_classes(color=color, size=size, caret=caret, nav=nav_like)
        menu_classes = dropdown_menu_classes(menu_variant=menu_variant, align_end=align_end)
        open_value = False if is_open is _UNSET or is_open is None else bool(is_open)
        _ensure_overlay_runtime()
        super().__init__(
            children=None,
            tag="li" if nav_like else "div",
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes(" ".join(root_classes))
        with self:
            toggle_tag = "a" if nav_like else "button"
            self._toggle = ui.element(toggle_tag).classes(" ".join(toggle_classes))
            self._toggle._props["data-ngbs-role"] = "toggle"
            self._toggle._props["aria-expanded"] = "true" if open_value else "false"
            self._toggle._props["aria-haspopup"] = "true"
            if nav_like:
                self._toggle._props["href"] = "#"
                self._toggle._props["role"] = "button"
            else:
                self._toggle._props["type"] = "button"
            if disabled:
                if nav_like:
                    self._toggle.classes(add="disabled")
                    self._toggle._props["aria-disabled"] = "true"
                    self._toggle._props["tabindex"] = "-1"
                else:
                    self._toggle._props["disabled"] = True
            if toggle_class_name:
                self._toggle.classes(toggle_class_name)
            _style_obj(self._toggle, toggle_style)
            text = "" if label is None else str(label)
            if hasattr(self._toggle, "set_text"):
                self._toggle.set_text(text)
            else:
                set_element_text(self._toggle, text)
            self._slot_host = ui.element("ul").classes(" ".join(menu_classes))
        self._children_passed = children is not None
        if children is not None:
            _adopt_into(self._slot_host, children, owner=self)
        self._on_item_click = None if on_item_click is _UNSET else on_item_click
        self._apply_open(open_value)
        _bind_kind(self, "dropdown", open=open_value, direction=direction)
        _wire_overlay_events(self)
        if on_toggle is not None:
            self.on("toggle", lambda _e=None: on_toggle())

    def _apply_open(self, value: bool) -> None:
        super()._apply_open(value)
        host = getattr(self, "_slot_host", None)
        if host is not None:
            if value:
                host.classes(add="show")
            else:
                host.classes(remove="show")
        toggle = getattr(self, "_toggle", None)
        if toggle is not None:
            toggle._props["aria-expanded"] = "true" if value else "false"


class _DropdownMenuItemImpl(_SlotRedirect, BootstrapElement):
    component_name = "DropdownMenuItem"
    styling_target = "root"
    reserved_classes = ("dropdown-item", "dropdown-header", "dropdown-divider")
    children_kind = "phrasing"

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        header: bool = False,
        divider: bool = False,
        disabled: bool = False,
        active: bool = False,
        href: str | None = None,
        n_clicks: int = 0,
        toggle: bool = True,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        if header and divider:
            raise PropConflictError("header/divider conflict")
        inner_classes = dropdown_item_inner_classes(
            header=header, divider=divider, disabled=disabled, active=active
        )
        super().__init__(
            children=None,
            tag="li",
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self._n_clicks = int(n_clicks)
        self._toggle = bool(toggle)
        self._disabled = bool(disabled)
        self._is_header = bool(header)
        self._is_divider = bool(divider)
        self._slot_host = None
        with self:
            if divider:
                ui.element("hr").classes(" ".join(inner_classes))
            elif header:
                self._slot_host = ui.element("h6").classes(" ".join(inner_classes))
            else:
                tag = "a" if href else "button"
                self._slot_host = ui.element(tag).classes(" ".join(inner_classes))
                if href:
                    self._slot_host._props["href"] = href
                else:
                    self._slot_host._props["type"] = "button"
                self._slot_host._props["data-ngbs-item-toggle"] = "true" if toggle else "false"
                if disabled:
                    self._slot_host._props["aria-disabled"] = "true"
                    self._slot_host._props["tabindex"] = "-1"
                    if href is None:
                        self._slot_host._props["disabled"] = True
                if active:
                    self._slot_host._props["aria-current"] = "true"
                self._slot_host.on("click", self._handle_click)
        self._children_passed = children is not None
        if children is not None and self._slot_host is not None:
            _fill_text_or_children(self._slot_host, children, owner=self)

    @property
    def n_clicks(self) -> int:
        return self._n_clicks

    @n_clicks.setter
    def n_clicks(self, value: int) -> None:
        self._n_clicks = int(value)

    def _handle_click(self, *_args: Any, **_kwargs: Any) -> None:
        if self._disabled or self._is_header or self._is_divider:
            return
        self._n_clicks += 1
        parent = _find_ancestor(self, "DropdownMenu")
        if parent is None:
            return
        callback = getattr(parent, "_on_item_click", None)
        if callback is not None:
            callback(self)
        if self._toggle:
            closer = getattr(parent, "close", None)
            if callable(closer):
                closer()


class _AccordionItemImpl(_SlotRedirect, BootstrapElement):
    component_name = "AccordionItem"
    styling_target = "root"
    reserved_classes = ("accordion-item",)
    children_kind = "auto"

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        title: str | None = None,
        item_id: str | None = None,
        class_name: str | None = None,
        title_class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        super().__init__(
            children=None,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes("accordion-item")
        self._item_id = item_id
        self._expanded = False
        with self:
            self._header = ui.element("h2").classes("accordion-header")
            with self._header:
                self._button = ui.element("button").classes("accordion-button collapsed")
                self._button._props["type"] = "button"
                self._button._props["aria-expanded"] = "false"
                if title_class_name:
                    self._button.classes(title_class_name)
                if title is not None:
                    if hasattr(self._button, "set_text"):
                        self._button.set_text(str(title))
                    else:
                        set_element_text(self._button, str(title))
            self._collapse = ui.element("div").classes("accordion-collapse collapse")
            self._collapse._props["role"] = "region"
            with self._collapse:
                self._slot_host = ui.element("div").classes("accordion-body")
        self._children_passed = children is not None
        if children is not None:
            _adopt_into(self._slot_host, children, owner=self)
        self._button.on("click", self._on_header_click)
        if self._item_id:
            self._bind_accordion_ids()

    @property
    def item_id(self) -> str | None:
        return self._item_id

    def _bind_accordion_ids(self) -> None:
        ident = self._item_id or "item"
        collapse_id = f"{ident}-collapse"
        header_id = f"{ident}-header"
        self._header._props["id"] = header_id
        self._collapse._props["id"] = collapse_id
        self._button._props["aria-controls"] = collapse_id
        self._collapse._props["aria-labelledby"] = header_id

    def _set_expanded(self, expanded: bool) -> None:
        self._expanded = bool(expanded)
        if self._expanded:
            self._button.classes(remove="collapsed")
            self._button._props["aria-expanded"] = "true"
            self._collapse.classes(add="show")
        else:
            self._button.classes(add="collapsed")
            self._button._props["aria-expanded"] = "false"
            self._collapse.classes(remove="show")
        for node in (self._button, self._collapse):
            updater = getattr(node, "update", None)
            if callable(updater):
                updater()

    def _on_header_click(self, *_args: Any, **_kwargs: Any) -> None:
        parent = _find_ancestor(self, "Accordion")
        ident = self._item_id
        if parent is not None and ident:
            parent._toggle_item(ident)
            return
        self._set_expanded(not self._expanded)


class _AccordionImpl(BootstrapElement):
    component_name = "Accordion"
    styling_target = "root"
    reserved_classes = ("accordion", "accordion-flush")
    children_kind = "grouping"

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        active_item: str | list[str] | None = None,
        always_open: bool = False,
        start_collapsed: bool = False,
        flush: bool = False,
        persist: str = "off",
        on_change: Callable[..., Any] | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        struct = accordion_structural_classes(flush=flush)
        super().__init__(
            children=children,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes(" ".join(struct))
        self._active_item_arg = active_item
        self._start_collapsed = bool(start_collapsed)
        self._always_open = bool(always_open)
        self._on_change = on_change
        self._persist = persist
        self._items: list[Any] = []
        self._active_item: str | list[str] | None = [] if self._always_open else None
        self._finalize_items()

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> Any:
        result = super().__exit__(exc_type, exc, tb)
        self._finalize_items()
        return result

    def _item_ids(self) -> list[str]:
        return [
            ident for ident in (getattr(item, "_item_id", None) for item in self._items) if ident
        ]

    def _finalize_items(self) -> None:
        items = _collect_accordion_items(self)
        given = [getattr(item, "_item_id", None) for item in items]
        ids = generate_accordion_item_ids(given)
        for item, ident in zip(items, ids, strict=True):
            item._item_id = ident
            bind = getattr(item, "_bind_accordion_ids", None)
            if callable(bind):
                bind()
        default_first = (not self._start_collapsed) and (self._active_item_arg is None)
        self._items = items
        self._active_item = resolve_accordion_active(
            self._active_item_arg,
            always_open=self._always_open,
            item_ids=ids,
            default_first=default_first,
        )
        self._sync_item_expanded()

    def _sync_item_expanded(self) -> None:
        active = self._active_item
        selected: set[str]
        if self._always_open:
            values = active if isinstance(active, list) else ([] if active is None else [active])
            selected = set(values)
        else:
            selected = {active} if isinstance(active, str) and active else set()
        for item in self._items:
            ident = getattr(item, "_item_id", None)
            setter = getattr(item, "_set_expanded", None)
            if callable(setter):
                setter(ident in selected)

    def _toggle_item(self, item_id: str) -> None:
        if self._always_open:
            current = list(self._active_item or [])
            if item_id in current:
                current.remove(item_id)
            else:
                current.append(item_id)
            self.active_item = current
            return
        self.active_item = None if self._active_item == item_id else item_id

    @property
    def active_item(self) -> str | list[str] | None:
        return self._active_item

    @active_item.setter
    def active_item(self, value: str | list[str] | None) -> None:
        resolved = resolve_accordion_active(
            value,
            always_open=self._always_open,
            item_ids=self._item_ids(),
            default_first=False,
        )
        if resolved == self._active_item:
            return
        self._active_item = resolved
        self._sync_item_expanded()
        if self._on_change is not None:
            self._on_change(resolved)

    @property
    def always_open(self) -> bool:
        return self._always_open

    @always_open.setter
    def always_open(self, value: bool) -> None:
        value = bool(value)
        if value == self._always_open:
            return
        current = self._active_item
        self._always_open = value
        if value:
            self._active_item = (
                [] if current is None else current if isinstance(current, list) else [current]
            )
        else:
            self._active_item = (
                (current[0] if current else None) if isinstance(current, list) else current
            )
        self._sync_item_expanded()


class _TooltipImpl(_OpenMixin, BootstrapElement):
    component_name = "Tooltip"
    styling_target = "root"
    reserved_classes = ("tooltip",)

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        target: str | BootstrapElement | None = None,
        placement: str = "auto",
        trigger: str | None = None,
        delay: dict[str, Any] | int | None = None,
        is_open: bool | None = None,
        autohide: bool | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        if target is None:
            raise TypeError("Tooltip requires target")
        _ensure_overlay_runtime()
        super().__init__(
            children=children,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        if isinstance(target, str):
            target_kind = "public"
            target_spec = target
        else:
            target_kind = "eid"
            target_spec = str(getattr(target, "id", target))
        self._apply_open(bool(is_open) if is_open is not None else False)
        _bind_kind(
            self,
            "tooltip",
            target=target_spec,
            target_kind=target_kind,
            placement=placement,
            trigger=trigger or "hover focus",
            autohide=True if autohide is None else bool(autohide),
            open=bool(is_open) if is_open is not None else False,
        )
        if delay is not None:
            self._props["data-ngbs-delay"] = (
                json.dumps(delay) if isinstance(delay, dict) else str(delay)
            )
        _portal_to_overlay_root(self)

    def _handle_delete(self) -> None:
        super()._handle_delete()


Modal, DbcModal = _make_surfaces(_ModalImpl)
ModalHeader, DbcModalHeader = _make_surfaces(_ModalHeaderImpl)
ModalTitle, DbcModalTitle = _make_surfaces(_ModalTitleImpl)
ModalBody, DbcModalBody = _make_surfaces(_ModalBodyImpl)
ModalFooter, DbcModalFooter = _make_surfaces(_ModalFooterImpl)
Collapse, DbcCollapse = _make_surfaces(_CollapseImpl)
Fade, DbcFade = _make_surfaces(_FadeImpl)
Offcanvas, DbcOffcanvas = _make_surfaces(_OffcanvasImpl)
DropdownMenu, DbcDropdownMenu = _make_surfaces(_DropdownMenuImpl)
DropdownMenuItem, DbcDropdownMenuItem = _make_surfaces(_DropdownMenuItemImpl)
Accordion, DbcAccordion = _make_surfaces(_AccordionImpl)
AccordionItem, DbcAccordionItem = _make_surfaces(_AccordionItemImpl)
Tooltip, DbcTooltip = _make_surfaces(_TooltipImpl)

modal = Modal
modal_header = ModalHeader
modal_title = ModalTitle
modal_body = ModalBody
modal_footer = ModalFooter
collapse = Collapse
fade = Fade
offcanvas = Offcanvas
dropdown_menu = DropdownMenu
dropdown_menu_item = DropdownMenuItem
accordion = Accordion
accordion_item = AccordionItem
tooltip = Tooltip

__all__ = [
    "Modal",
    "DbcModal",
    "modal",
    "ModalHeader",
    "DbcModalHeader",
    "modal_header",
    "ModalTitle",
    "DbcModalTitle",
    "modal_title",
    "ModalBody",
    "DbcModalBody",
    "modal_body",
    "ModalFooter",
    "DbcModalFooter",
    "modal_footer",
    "Collapse",
    "DbcCollapse",
    "collapse",
    "Fade",
    "DbcFade",
    "fade",
    "Offcanvas",
    "DbcOffcanvas",
    "offcanvas",
    "DropdownMenu",
    "DbcDropdownMenu",
    "dropdown_menu",
    "DropdownMenuItem",
    "DbcDropdownMenuItem",
    "dropdown_menu_item",
    "Accordion",
    "DbcAccordion",
    "accordion",
    "AccordionItem",
    "DbcAccordionItem",
    "accordion_item",
    "Tooltip",
    "DbcTooltip",
    "tooltip",
    "accordion_structural_classes",
    "collapse_structural_classes",
    "dropdown_direction_class",
    "dropdown_item_inner_classes",
    "dropdown_menu_classes",
    "dropdown_root_classes",
    "dropdown_toggle_classes",
    "fade_structural_classes",
    "generate_accordion_item_ids",
    "modal_dialog_classes",
    "offcanvas_structural_classes",
    "resolve_accordion_active",
]

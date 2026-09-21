# Keyboard & Accessibility Release Checklist

- [ ] Tab order reaches every interactive control
- [ ] Escape closes Modal/Offcanvas/DropdownMenu/Popover/Tooltip
- [ ] Arrow keys move within Tabs (`ArrowLeft`/`ArrowRight`/`Home`/`End`)
- [ ] Focus returns to the triggering element on close
- [ ] Dialogs trap focus while open
- [ ] `role`/`aria-*` present per component page (tablist/tab/tabpanel, dialog/modal, tooltip)
- [ ] Visible focus styles intact in light AND dark modes
- [ ] Reduced-motion: transitions degrade safely

How to run: manual pass on the demo service plus `pytest --visual` matrix when
baselines exist. Overlay z-index policy: backdrop 5040 / modal 5055 / tooltip 5090.

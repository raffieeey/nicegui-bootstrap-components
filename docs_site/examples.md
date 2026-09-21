# Examples

Worked examples for the Bootstrap 5.3 component surface. Source lives under
`examples/` and is grouped into component demonstrations, gallery apps, and
page templates. Every file in the tree is listed in `examples/manifest.yaml`
and served by the demo service (`python -m demo.main`).

## Component demonstrations

Small, single-purpose snippets. Each defines a `demo()` that the smoke tests
import and execute.

- `examples/components/accordion/always_open.py` — Accordion with several items open at once.
- `examples/components/accordion/simple.py` — Accordion with rich panel content.
- `examples/components/accordion/collapsed.py` — Accordion where every panel starts closed.
- `examples/components/accordion/flush.py` — Flush accordion.
- `examples/components/accordion/callback.py` — Accordion reporting the open item.
- `examples/components/accordion/always_open_callback.py` — Always-open accordion with a callback.
- `examples/components/alert/dismissible.py` — Dismissible alerts.
- `examples/components/alert/simple.py` — Alerts in every contextual color.
- `examples/components/alert/link.py` — Alerts with a color-matched link.
- `examples/components/alert/content.py` — Alert with heading, paragraphs, and divider.
- `examples/components/alert/auto_dismiss.py` — Auto-dismissing alert.
- `examples/components/alert/icon.py` — Alerts with leading icons.
- `examples/components/badge/simple.py` — Badges as counters.
- `examples/components/badge/size.py` — Badges that scale with their parent.
- `examples/components/badge/color.py` — Badge background colors.
- `examples/components/badge/text_color.py` — Badge text colors.
- `examples/components/badge/pills.py` — Pill badges.
- `examples/components/badge/positioned.py` — Badge positioned in a button corner.
- `examples/components/badge/links.py` — Badges rendered as links.
- `examples/components/breadcrumb/basic.py` — Basic breadcrumb.
- `examples/components/breadcrumb/item_styling.py` — Breadcrumb item styling.
- `examples/components/button/colors.py` — Button color variants.
- `examples/components/button/outline_sizes.py` — Outline buttons and size variants.
- `examples/components/button/basic.py` — Basic buttons.
- `examples/components/button/link_buttons.py` — Link-styled buttons.
- `examples/components/button/outline_size_state.py` — Outline, size, and state buttons.
- `examples/components/button_group/basic.py` — Basic button group.
- `examples/components/button_group/size_and_vertical.py` — Button group size and vertical layout.
- `examples/components/card/basic_body.py` — Card with a basic body.
- `examples/components/card/colored_outline.py` — Colored outline cards.
- `examples/components/card/group_composition.py` — Card group composition.
- `examples/components/carousel/basic.py` — Basic carousel.
- `examples/components/carousel/controls_indicators_interval.py` — Carousel with controls, indicators, and interval.
- `examples/components/collapse/basic_usage.py` — Basic collapse usage.
- `examples/components/collapse/dimension_navbar.py` — Collapse dimension and navbar.
- `examples/components/dropdown_menu/basic_usage.py` — Basic dropdown menu usage.
- `examples/components/dropdown_menu/direction_and_navbar.py` — Dropdown direction and navbar.
- `examples/components/form/basic_usage.py` — Basic form usage.
- `examples/components/form/form_floating.py` — Floating form labels.
- `examples/components/form/validation_feedback.py` — Form validation feedback.
- `examples/components/input/debounce_modes.py` — Input debounce modes.
- `examples/components/input/labeled_name.py` — Labeled name input.
- `examples/components/input/placeholder_type_size.py` — Input placeholder, type, and size.
- `examples/components/input_group/amount_currency.py` — Amount and currency input group.
- `examples/components/input_group/size_lg_url.py` — Large URL input group.
- `examples/components/input_group/username_prefix.py` — Username prefix input group.
- `examples/components/jumbotron/alternate_recipe.py` — Alternate jumbotron recipe.
- `examples/components/jumbotron/basic.py` — Basic jumbotron recipe.
- `examples/components/layout/grid_breakpoints.py` — Container, Row, Col, and breakpoints.
- `examples/components/layout/simple.py` — Basic Container, Row, and Col usage.
- `examples/components/layout/width.py` — Column width options.
- `examples/components/layout/order_offset.py` — Reordering and offsetting columns.
- `examples/components/layout/breakpoints.py` — Widths per screen size.
- `examples/components/layout/no_gutters.py` — A row without gutters.
- `examples/components/layout/vertical.py` — Vertical column alignment.
- `examples/components/layout/horizontal.py` — Horizontal column alignment.
- `examples/components/layout/grid_only.py` — Grid-only stylesheet.
- `examples/components/layout/simple_stack.py` — Vertical stacks.
- `examples/components/layout/horizontal_stack.py` — Horizontal stacks.
- `examples/components/layout/stack_spacers.py` — Stacks with spacing utilities.
- `examples/components/list_group/basic.py` — Basic list group.
- `examples/components/list_group/flush.py` — Flush list group.
- `examples/components/list_group/numbered.py` — Numbered list group.
- `examples/components/modal/static_backdrop.py` — Modal with a static backdrop.
- `examples/components/modal/confirm_publish.py` — Confirm publish modal.
- `examples/components/nav/basic.py` — Basic nav.
- `examples/components/nav/vertical.py` — Vertical nav.
- `examples/components/navbar/fixed_sticky.py` — Fixed and sticky navbars.
- `examples/components/offcanvas/basic.py` — Basic offcanvas.
- `examples/components/offcanvas/placement_end.py` — End-placed offcanvas.
- `examples/components/pagination/basic.py` — Basic pagination.
- `examples/components/pagination/generated_items.py` — Pagination with generated items.
- `examples/components/pagination/size_and_alignment.py` — Pagination size and alignment.
- `examples/components/placeholder/animation.py` — Placeholder animation.
- `examples/components/placeholder/basic.py` — Basic placeholder.
- `examples/components/placeholder/size.py` — Placeholder sizes.
- `examples/components/popover/basic_usage.py` — Basic popover usage.
- `examples/components/popover/header_body.py` — Popover with header and body.
- `examples/components/popover/target_id.py` — Popover targeting an element id.
- `examples/components/progress/basic_usage.py` — Basic progress bar.
- `examples/components/progress/color.py` — Colored progress bars.
- `examples/components/progress/stacked.py` — Stacked progress bars.
- `examples/components/spinner/fullscreen.py` — Fullscreen spinner.
- `examples/components/tabs/card_tabs.py` — Tabs in card mode.
- `examples/components/tabs/no_ids.py` — Tabs without explicit ids.
- `examples/components/tabs/active_tab_on_change.py` — Tabs with active tab on change.
- `examples/components/tabs/basic_usage.py` — Basic tabs usage.
- `examples/components/tabs/composition.py` — Tabs composition.
- `examples/components/tabs/with_card.py` — Tabs with a card.
- `examples/components/toast/dismiss_options.py` — Toast dismiss and duration options.
- `examples/components/toast/basic_usage.py` — Basic toast usage.
- `examples/components/toast/open_state.py` — Toast open state.
- `examples/components/table/basic.py` — Basic striped, bordered, hover table.
- `examples/components/table/options.py` — Table visual option combinations.
- `examples/components/table/dataframe.py` — Table built from a pandas DataFrame.
- `examples/components/tooltip/basic.py` — Basic tooltip.
- `examples/components/tooltip/delay.py` — Tooltip delay.
- `examples/components/tooltip/target.py` — Tooltip target.

## Gallery apps

Fuller applications with their own `main.py` entry point.

- `examples/gallery/iris/main.py` — Iris k-means demo (Container, Row, Col, Card, Select, Table).
- `examples/gallery/graphs_in_tabs/main.py` — Charts hosted in Tabs.
- `examples/gallery/simple_sidebar/main.py` — Sidebar navigation with a content pane.

## Page templates

Multi-page layouts. Each defines `page_*` functions that build a full page,
so the smoke tests execute them directly.

- `examples/templates/simple_sidebar.py` — Fixed left sidebar with three pages.
- `examples/templates/navbar.py` — Top navbar layout with two pages.
- `examples/templates/responsive_sidebar.py` — Sidebar that stacks on small screens.
- `examples/templates/responsive_collapsible_sidebar.py` — Responsive sidebar with a collapse toggle.
- `examples/templates/sidebar_with_submenus.py` — Sidebar with collapsible submenus.
- `examples/templates/collapsible_sidebar_with_icons.py` — Collapsible icon sidebar.

!!! note

    Live previews run on the demo service (`python -m demo.main`) and static
    docs show source and captured rendered previews.

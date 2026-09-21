# Progress

Progress renders one or more Bootstrap 5 progress bars. Use it for determinate
completion (uploads, wizards, batch jobs) where the filled portion of the bar
should reflect real work.

A single bar is enough for one metric. Stack several bars in one track when you are
showing parts of a whole, such as success / warning / remaining.

## Basic usage

{{example:examples/components/progress/basic_usage.py:demo}}

Place the control next to the label that names the job it represents. A bar without
copy is hard to interpret, especially when several jobs run at once.

## Options

### Color

`color` applies a Bootstrap theme color to the filled portion. `primary` and
`info` read as in-progress, `success` as complete, `warning` and `danger` as
attention. Keep the color aligned with the meaning of the metric, not with nearby
branding, so two bars on the same page stay comparable.

{{example:examples/components/progress/color.py:demo}}

### Striped and animated

`striped` paints the Bootstrap stripe pattern on the bar. `animated` moves those
stripes, which signals that work is still happening even if the filled width has
not changed. Use animation for live jobs; turn it off for a snapshot (for example a
quota that only updates daily).

Stripes without animation are a static texture. Animation without stripes has
nothing to move, so the two flags are normally turned on together for an in-flight
bar.

### Stacked bars

Nest multiple `Progress` children inside a parent `Progress` to stack segments in
one track. Each child takes its own `color`, `striped`, and `animated` flags.
Widths can be hinted with `class_name` utilities so the segments add up to the
parent track.

{{example:examples/components/progress/stacked.py:demo}}

Stacked bars are for parts of one whole, not for unrelated jobs. Independent jobs
belong in separate tracks with their own labels.

### When to prefer a spinner

If you cannot measure completion, a Spinner is clearer than an animated bar that
never moves. Progress implies a known total; do not use it as a generic busy
indicator.

## Argument reference

{{apidoc:Progress}}

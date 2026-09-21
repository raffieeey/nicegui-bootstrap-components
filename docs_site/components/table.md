# Table

Table renders Bootstrap 5 table markup for tabular data. It is the right host for
rows and columns that need scanability: striped rows, borders, hover highlighting,
and an optional responsive wrapper that scrolls on narrow viewports.

Use Table when the data is inherently grid-shaped. Do not force a table on a
definition list or a card grid just to get stripes.

## Basic usage

{{example:examples/components/table/basic.py:demo}}

Fill the table with the row content your application already has, or build it from
a pandas DataFrame with `from_dataframe` as shown below. The visual flags below
compose independently.

## Options

### Striped, bordered, hover

`striped` alternates row backgrounds so wide grids are easier to track. `bordered`
draws cell borders, which helps when columns are dense or numeric. `hover`
highlights the row under the pointer so selection and scan paths are obvious.

{{example:examples/components/table/options.py:demo}}

Turn on only what the data needs. Stripes plus borders plus hover on a small two-
column table is heavier than the content.

### Responsive

`responsive` wraps the table so horizontal overflow scrolls inside the wrapper
instead of stretching the page. Enable it whenever the column count can exceed a
phone width. Pair it with `hover` so the row highlight still tracks while the user
scrolls sideways.

### Building from a DataFrame

`Table.from_dataframe` builds header and body rows from a pandas DataFrame. Pandas
is an optional dependency; install the examples extra before you call it:

`pip install nicegui-bootstrap-components[examples]`

{{example:examples/components/table/dataframe.py:demo}}

The DataFrame columns become the header labels, in order. Clean the frame (column
names, dtypes, row order) before you pass it in; the helper does not try to guess a
presentation layer on top of pandas.

`from_dataframe` still accepts the same visual flags as the constructor, so a
DataFrame-backed table can be striped, bordered, hoverable, and responsive without
a second wrapper.

## Argument reference

{{apidoc:Table}}

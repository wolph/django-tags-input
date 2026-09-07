# Try the forms

Choose an example, add a few tags, then save. The widget sends the labels to
a real Django form running in a Python worker in your browser. SQLite stores
the relationships in the order returned by `TagsInputFormMixin`.

```{raw} html
<iframe src="_static/playground/index.html" title="Interactive Django tags input form" style="width:100%;height:950px;border:0;border-radius:12px" loading="lazy"></iframe>
```

```{raw} html
<p><a href="_static/playground/index.html" target="_blank" rel="noopener">Open the example in its own tab</a></p>
```

## Three things to try

1. In **Create missing tags**, add `Weekend project` and save. Reload the page.
   The new object and your selected order remain in this browser.
2. In **Choose existing tags only**, select an autocomplete result. A label
   outside the permitted queryset fails Django validation.
3. In **Combine contact fields**, type `Ada` and select `Ada - Lovelace`.
   The visible label comes from two model fields.

Saved values and unfinished tag selections are separate. A failed save keeps
the previous database values. Reset restores the seeded example data across
these documentation pages and prevents an older tab from saving stale data.

> [!NOTE]
> The first start downloads Python, Django and the package from this documentation
> build. Entered tags stay in your browser. If browser storage is unavailable,
> choose a temporary session. Its changes disappear when the page closes.

## Use the same forms locally

The browser uses the `showcase` app from this repository. Run it locally to
inspect requests, use the Django admin or change the models. See
{doc}`example-project` for setup commands.

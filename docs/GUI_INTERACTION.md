# GUI Interaction

Defines framework-independent state for viewport, selection, layers, active tools, hit testing, measurement and shortcuts. The model can back Tkinter now and a richer GUI later.

## Confidence heatmap

The evidence viewer can optionally color tracks and pads by the confidence of their existing physical `NetGroup`.

The visualization is review-only:

- it does not modify reconstructed confidence values;
- it does not infer confidence for objects that have no physical-net evidence;
- missing or non-finite confidence remains `unknown`;
- the displayed buckets are explicit UI ranges only: `>= 0.90`, `0.70-0.89`, `< 0.70`, and `unknown`;
- selecting an object exposes the exact physical-net confidence and its source in `review_context`.

Outlines are shown as neutral/unknown in heatmap mode because they do not carry physical-net confidence.

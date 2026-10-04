# Correction log

An honest record of what was wrong and what fixed it. Kept short and factual.

---

## Architecture / specification

The agent was asked to design a 2-bedroom terraced house from scratch. Multiple
proposals were rejected:

| Problem | Example |
|---|---|
| Bedroom unusable | Second bedroom 1.20 m deep, 4.92 m² |
| Landing oversized | Landing larger than the rooms it served |
| Stair did not fit | 3.60 m run drawn into a 2.60 m opening, with "the remainder continues into the landing" |
| Area did not add up | 29.02 m² of rooms in a 48.96 m² envelope, difference called "partitions" |
| Party wall window | Bathroom window on the side wall of a stated mid-terrace |
| Figures disagreed | Room area printed on the image did not match the geometry |
| Overlap | Stair treads drawn through the WC |
| Bathroom too small | 0.85 m wide |
| Misplaced windows | Two front windows specified at overlapping X ranges |

**Fix:** the human side defined the envelope, room count, room sizes and stair
position. The agent then converted that agreed layout into coordinates. The
downstairs WC was dropped because it could not be fitted without damaging the
house.

The agent's recurring failure mode was responding to a rejected proposal by
starting another redesign instead of applying the specific feedback.

---

## Blender / rendering

### The black render

The first render produced a PNG that was almost entirely black.

**Cause:** the world background had been set to black while `color_type` was
switched between `OBJECT` and `MATERIAL`. The frame was filled by the background,
not by geometry.

**Why it was not caught:** verification checked that the file existed, was not
uniform, and contained both black and white pixels. All three passed on a blank
image. That is not visual verification.

### The blank white render

After fixing the background, the image was still blank.

**Cause:** the two floors were modelled stacked vertically. The top-down
orthographic camera saw only the upper surface of the first-floor slab, so the
ground floor was completely occluded.

**Fix:** both plans drawn side by side at the same Z level. A drawing convention
only — no room, dimension or coordinate was changed.

### Script typos introduced during repair

While repairing the script, two classes of typo were introduced and then caught by
actually running it:

- `integral_depth` / `integral_width` instead of `internal_depth` / `internal_width`
  — 8 occurrences
- `add_opinion_box` instead of `add_opening_box` — 7 occurrences

Both produced `NameError` on execution, which is how they were found. Textual
review had not caught them.

---

## What the lesson actually was

Two separate things were conflated for a long stretch:

1. **Was the render produced?** — answered by the log, and yes.
2. **Was the render correct?** — only answerable by looking at it.

Checking the first repeatedly produced false confidence about the second.
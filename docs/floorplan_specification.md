# Floor plan specification — simple 2-bedroom UK terrace

This is the specification that the final render was generated from. It is
included so the Blender geometry can be checked against a written description.

**External footprint**: 5.50 m × 10.00 m
**External wall thickness**: 0.20 m
**Internal partition thickness**: 0.10 m
**Internal clear envelope**: 5.10 m × 9.60 m = 48.96 m² per storey
**Storey-to-storey height**: 2.80 m
**No downstairs WC**
**Mid-terrace**: only front and rear elevations carry windows and doors.

Coordinates are relative to the inner face of the external walls.
X runs left→right, Y runs front→rear, with Y = 0 at the street elevation.

---

## Ground floor

| Zone | X (m) | Y (m) | Width × Depth | Area |
|------|-------|-------|---------------|------|
| Living room | 0.00 – 5.10 | 0.00 – 3.20 | 5.10 × 3.20 m | 16.32 m² |
| Stair | 0.00 – 1.00 | 3.20 – 6.40 | 1.00 × 3.20 m | 3.20 m² |
| Hall | 1.00 – 5.10 | 3.20 – 6.40 | 4.10 × 3.20 m | 13.12 m² |
| Kitchen / dining | 0.00 – 5.10 | 6.40 – 9.60 | 5.10 × 3.20 m | 16.32 m² |

**Openings**
- Front door: front wall, X 0.50 – 1.40 (0.90 m)
- Living room windows: front wall, X 2.60 – 3.80 and X 4.10 – 5.00 (0.90 m each)
- Rear door: rear wall, X 1.10 – 2.00 (0.90 m)
- Kitchen windows: rear wall, X 2.60 – 3.80 and X 4.10 – 5.00 (0.90 m each)
- Stairwell window: rear wall, X 0.30 – 1.10 (0.70 m)

---

## First floor

| Zone | X (m) | Y (m) | Width × Depth | Area |
|------|-------|-------|---------------|------|
| Bedroom 1 | 0.00 – 3.00 | 0.00 – 3.20 | 3.00 × 3.20 m | 9.60 m² |
| Stair void | 0.00 – 1.00 | 0.00 – 3.20 | 1.00 × 3.20 m | 3.20 m² |
| Bathroom | 0.00 – 2.00 | 3.20 – 5.40 | 2.00 × 2.20 m | 4.40 m² |
| Landing | 2.00 – 5.10 | 3.20 – 5.40 | 3.10 × 2.20 m | 6.82 m² |
| Landing (rear strip) | 0.00 – 5.10 | 5.40 – 6.40 | 5.10 × 1.00 m | 5.10 m² |
| Bedroom 2 | 0.00 – 5.10 | 6.40 – 9.60 | 5.10 × 3.20 m | 16.32 m² |

**Openings**
- Bedroom 1 windows: front wall, X 2.60 – 3.80 and X 4.10 – 5.00 (0.90 m each)
- Bedroom 2 windows: rear wall, X 2.60 – 3.80 and X 4.10 – 5.00 (0.90 m each)
- Landing window: rear wall, X 0.30 – 1.10 (0.70 m)
- Bathroom: lit by a rooflight, no wall opening (mid-terrace has no side windows)

**Doors** (all internal, 0.80 m)
- Bedroom 1: at Y 1.20 – 2.00 off the landing
- Bathroom: at Y 3.90 – 4.70
- Bedroom 2: at Y 6.60 – 7.40

---

## Staircase

Straight single flight, 1.00 m wide, in the X 0.00 – 1.00 / Y 3.20 – 6.40 well.

| Property | Value |
|----------|-------|
| Floor-to-floor rise | 2.80 m |
| Risers | 15 |
| Rise per step | 0.187 m |
| Going per step | 0.213 m |
| Total horizontal run | 3.20 m |
| 2R + G | 0.587 m |

---

## Notes and known limitations

1. This is an **illustrative concept**, not architect-certified and not checked
   against Building Regulations.
2. The final presentation draws both floors as flat plans **side by side at the same
   Z level**. A stacked 3D model cannot be read from directly above, because the
   first-floor slab hides the ground floor. The room coordinates above are the real
   house coordinates; only the drawing convention differs.
3. Room rectangles tile the internal envelope without overlap. Wall footprints are
   not included in the room areas — they are the boundaries between rooms.
4. No furniture, fixtures or sanitary ware are modelled, by design.
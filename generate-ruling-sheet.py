#!/usr/bin/env python3
"""
guide_sheet.py — generate a printable ruling guide sheet to slip UNDER
translucent paper (Tomoe River, Midori MD, etc.). Lines are pure black so
they show through the sheet on top.

Requires:  pip install reportlab
"""

import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# ----- reference dimensions, portrait, (width_mm, height_mm) -----------------
REAL_ESTATE = {
    "A6":     (105.0, 148.0),
    "A5":     (148.0, 210.0),
    "B5-ISO": (176.0, 250.0),   # ISO 216 B5
    "B5-JIS": (182.0, 257.0),   # JIS B5 (Japanese notebooks)
    "B5":     (176.0, 250.0),   # alias -> ISO B5
}

PHYSICAL_PAGE = {
    "A6":     (105.0, 148.0),
    "A5":     (148.0, 210.0),
    "B5":     (176.0, 250.0),
    "A4":     (210.0, 297.0),
    "LETTER": (215.9, 279.4),
    "LEGAL":  (215.9, 355.6),
}

RULING_CHOICES = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5]
EPS = 1e-6


def _clip(v, lo, hi):
    return max(lo, min(hi, v))


def draw_crop_marks(c, tx0, ty0, tx1, ty1, page_w, page_h, gap, width):
    """Draw crop marks that run to the page edges, but ONLY along trim edges
    that are interior to the page. Anything off-page is clipped away, so a
    flush top-left layout yields marks along the right & bottom cuts only."""
    c.setDash()
    c.setLineWidth(width)

    interior_left   = tx0 > EPS
    interior_right  = tx1 < page_w - EPS
    interior_bottom = ty0 > EPS
    interior_top    = ty1 < page_h - EPS

    def vline(x, ya, yb):
        ya, yb = _clip(ya, 0, page_h), _clip(yb, 0, page_h)
        if abs(yb - ya) > EPS:
            c.line(x * mm, ya * mm, x * mm, yb * mm)

    def hline(y, xa, xb):
        xa, xb = _clip(xa, 0, page_w), _clip(xb, 0, page_w)
        if abs(xb - xa) > EPS:
            c.line(xa * mm, y * mm, xb * mm, y * mm)

    # vertical cut lines (left/right) -> vertical marks above & below trim box
    for x, interior in ((tx0, interior_left), (tx1, interior_right)):
        if interior:
            vline(x, ty1 + gap, page_h)   # extend up to top edge
            vline(x, ty0 - gap, 0)        # extend down to bottom edge
    # horizontal cut lines (bottom/top) -> horizontal marks left & right of box
    for y, interior in ((ty0, interior_bottom), (ty1, interior_top)):
        if interior:
            hline(y, tx1 + gap, page_w)   # extend right to right edge
            hline(y, tx0 - gap, 0)        # extend left to left edge


def build_guide(args):
    page_w, page_h = PHYSICAL_PAGE[args.page]
    re_w, re_h     = REAL_ESTATE[args.size]

    if re_w > page_w + EPS or re_h > page_h + EPS:
        raise SystemExit(
            f"Real estate {args.size} ({re_w}x{re_h} mm) does not fit on "
            f"page {args.page} ({page_w}x{page_h} mm)."
        )

    # position the real estate on the physical page
    if args.center:                          # centered (printer-safe) mode
        re_x0 = (page_w - re_w) / 2.0
        re_y0 = (page_h - re_h) / 2.0
    else:                                    # DEFAULT: flush to top-left -> 2 cuts
        re_x0 = 0.0
        re_y0 = page_h - re_h

    # margins as fractions of the real-estate dimensions
    top_m    = re_h * (1.0 / 9.0)
    bottom_m = re_h * (2.0 / 9.0)
    if args.undersheet == "right":          # default: wide margin on the right
        left_m, right_m = re_w * (1.0 / 9.0), re_w * (2.0 / 9.0)
    else:                                   # left undersheet -> swap L/R
        left_m, right_m = re_w * (2.0 / 9.0), re_w * (1.0 / 9.0)

    # writing area, page coordinates (mm). reportlab origin = bottom-left.
    wa_x0 = re_x0 + left_m
    wa_x1 = re_x0 + re_w - right_m
    wa_y0 = re_y0 + bottom_m
    wa_y1 = re_y0 + re_h - top_m

    out = args.output or (
        f"guide_{args.size}_{args.ruling:g}mm_{args.undersheet}_"
        f"{'center' if args.center else 'flush'}_{args.page}.pdf"
    )

    c = canvas.Canvas(out, pagesize=(page_w * mm, page_h * mm))
    c.setTitle(f"Guide {args.size} {args.ruling:g}mm {args.undersheet}-undersheet")
    c.setStrokeColorRGB(0, 0, 0)            # pure black = darkest show-through
    c.setFillColorRGB(0, 0, 0)

    # 1) real-estate outline (alignment/trim aid) — solid, thin
    if not args.no_frame:
        c.setDash()                         # solid
        c.setLineWidth(args.frame_width)
        c.rect(re_x0 * mm, re_y0 * mm, re_w * mm, re_h * mm, stroke=1, fill=0)

    # 2) crop marks to the page edges (interior cut lines only)
    if not args.no_crop:
        draw_crop_marks(c, re_x0, re_y0, re_x0 + re_w, re_y0 + re_h,
                        page_w, page_h, args.crop_gap, args.crop_width)

    # 3) horizontal ruling lines — WRITING AREA ONLY
    c.setDash()                             # solid
    c.setLineWidth(args.ruling_width)
    spacing = args.ruling
    y = wa_y1 - spacing                      # first line one spacing below top
    while y > wa_y0 + EPS:                    # stop before the bottom border
        c.line(wa_x0 * mm, y * mm, wa_x1 * mm, y * mm)
        y -= spacing

    # 4) dashed border between margins and writing area — prominent
    c.setLineWidth(args.border_width)
    c.setDash(2.0 * mm, 1.5 * mm)            # 2 mm on, 1.5 mm off
    c.rect(wa_x0 * mm, wa_y0 * mm,
           (wa_x1 - wa_x0) * mm, (wa_y1 - wa_y0) * mm, stroke=1, fill=0)

    # 5) label in the (roomy) bottom margin: size + ruling + undersheet
    if not args.no_label:
        c.setDash()
        label = f"{args.size}  •  {args.ruling:g} mm  •  {args.undersheet}-undersheet"
        text_y = re_y0 + (bottom_m / 2.0) - (args.label_size / 2.0 / 72.0 * 25.4)
        c.setFont("Helvetica", args.label_size)
        c.drawCentredString(((wa_x0 + wa_x1) / 2.0) * mm, text_y * mm, label)

    c.showPage()
    c.save()
    print(f"Wrote {out}")


def parse_args():
    p = argparse.ArgumentParser(
        description="Ruling guide sheet for translucent paper.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python guide_sheet.py                       # A5, flush top-left, 2 cuts\n"
            "  python guide_sheet.py --center              # centered (printer-safe)\n"
            "  python guide_sheet.py --size B5-JIS --ruling 6.5\n"
            "  python guide_sheet.py --size A6 --crop-gap 0\n"
        ),
    )
    p.add_argument("--size", choices=REAL_ESTATE.keys(), default="A5",
                   help="Final trimmed paper size (the 'real estate').")
    p.add_argument("--ruling", type=float, choices=RULING_CHOICES, default=7.0,
                   metavar="MM", help="Ruling spacing in mm.")
    p.add_argument("--undersheet", choices=["right", "left"], default="right",
                   help="Wide margin side ('right' = right-undersheet default).")
    p.add_argument("--page", choices=PHYSICAL_PAGE.keys(), default="LETTER",
                   help="Physical sheet you print on.")
    p.add_argument("--center", action="store_true",
                   help="Center the real estate on the page (for printers with "
                        "edge-printing limits). Default is flush top-left = 2 cuts.")
    p.add_argument("--ruling-width", type=float, default=0.6, metavar="PT",
                   help="Ruling line width in points.")
    p.add_argument("--border-width", type=float, default=1.2, metavar="PT",
                   help="Dashed writing-area border width in points.")
    p.add_argument("--frame-width", type=float, default=0.5, metavar="PT",
                   help="Real-estate outline width in points.")
    p.add_argument("--no-frame", action="store_true",
                   help="Do not draw the real-estate outline.")
    # crop marks
    p.add_argument("--no-crop", action="store_true",
                   help="Do not draw crop/trim marks.")
    p.add_argument("--crop-gap", type=float, default=1.5, metavar="MM",
                   help="Gap between the trim corner and the crop mark "
                        "(set 0 to touch the trim line).")
    p.add_argument("--crop-width", type=float, default=0.5, metavar="PT",
                   help="Crop mark line width in points.")
    # label
    p.add_argument("--no-label", action="store_true",
                   help="Do not print the size/ruling label.")
    p.add_argument("--label-size", type=float, default=8.0, metavar="PT",
                   help="Label font size in points.")
    p.add_argument("--output", default=None, help="Output PDF filename.")
    return p.parse_args()


if __name__ == "__main__":
    build_guide(parse_args())

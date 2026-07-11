#!/usr/bin/env python3
"""
guide_sheet.py — generate a printable ruling guide sheet to slip UNDER
translucent paper (Tomoe River, Midori, etc.). Lines are pure black so
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


def draw_crop_marks(c, x0, y0, x1, y1, length_mm, gap_mm, width_pt):
    """L-shaped crop marks just outside each corner of the trim box."""
    c.setDash()
    c.setLineWidth(width_pt)
    L, g = length_mm, gap_mm
    corners = [
        # (corner_x, corner_y, x_dir, y_dir)  dir = outward direction
        (x0, y0, -1, -1),   # bottom-left
        (x1, y0, +1, -1),   # bottom-right
        (x0, y1, -1, +1),   # top-left
        (x1, y1, +1, +1),   # top-right
    ]
    for cx, cy, sx, sy in corners:
        # horizontal tick (extends outward in x)
        c.line((cx + sx * g) * mm, cy * mm, (cx + sx * (g + L)) * mm, cy * mm)
        # vertical tick (extends outward in y)
        c.line(cx * mm, (cy + sy * g) * mm, cx * mm, (cy + sy * (g + L)) * mm)


def build_guide(args):
    page_w, page_h = PHYSICAL_PAGE[args.page]
    re_w, re_h     = REAL_ESTATE[args.size]

    if re_w > page_w + 1e-6 or re_h > page_h + 1e-6:
        raise SystemExit(
            f"Real estate {args.size} ({re_w}x{re_h} mm) does not fit on "
            f"page {args.page} ({page_w}x{page_h} mm)."
        )

    # center the real estate on the physical page
    re_x0 = (page_w - re_w) / 2.0
    re_y0 = (page_h - re_h) / 2.0

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
        f"guide_{args.size}_{args.ruling:g}mm_{args.undersheet}_{args.page}.pdf"
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

    # 2) crop marks just outside the real-estate corners
    if not args.no_crop:
        draw_crop_marks(c, re_x0, re_y0, re_x0 + re_w, re_y0 + re_h,
                        args.crop_length, args.crop_gap, args.crop_width)

    # 3) horizontal ruling lines — WRITING AREA ONLY
    c.setDash()                             # solid
    c.setLineWidth(args.ruling_width)
    spacing = args.ruling
    eps = 1e-6
    y = wa_y1 - spacing                      # first line one spacing below top
    while y > wa_y0 + eps:                   # stop before the bottom border
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
        # vertically center the text within the bottom margin band
        text_y = re_y0 + (bottom_m / 2.0) - (args.label_size / 2.0 / 72.0 * 25.4)
        c.setFont("Helvetica", args.label_size)
        # center it under the writing area
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
            "  python guide_sheet.py                              # A5, 7mm, right-undersheet on LETTER\n"
            "  python guide_sheet.py --size B5-JIS --ruling 6.5\n"
            "  python guide_sheet.py --size B5-ISO --undersheet left\n"
            "  python guide_sheet.py --size A6 --page A6 --no-crop\n"
        ),
    )
    p.add_argument("--size", choices=REAL_ESTATE.keys(), default="A5",
                   help="Final trimmed paper size (the 'real estate').")
    p.add_argument("--ruling", type=float, choices=RULING_CHOICES, default=7.0,
                   metavar="MM", help="Ruling spacing in mm.")
    p.add_argument("--undersheet", choices=["right", "left"], default="right",
                   help="Wide margin side ('right' = right-undersheet default).")
    p.add_argument("--page", choices=PHYSICAL_PAGE.keys(), default="LETTER",
                   help="Physical sheet you print on; real estate is centered.")
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
    p.add_argument("--crop-length", type=float, default=4.0, metavar="MM",
                   help="Length of each crop mark tick.")
    p.add_argument("--crop-gap", type=float, default=1.5, metavar="MM",
                   help="Gap between the trim corner and the crop mark.")
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

# tcsh completions for generate-ruling-sheet.py
# Install: source this file from your ~/.tcshrc, e.g.
#   source /path/to/guide-sheet/completions/generate-ruling-sheet.tcsh
# (tcsh has no autoload dir like fish; it must be explicitly sourced)

# List possibilities on an ambiguous completion (e.g. hitting TAB on an
# empty/partial word) instead of just beeping. "ambiguous" means it only
# lists when TAB wouldn't add any new characters, so unique prefixes still
# complete silently. This is a GLOBAL tcsh setting, not scoped to this
# command -- remove this line if you don't want it to affect other commands.
set autolist = ambiguous

# NOTE: with lowercase 'c/--/LIST/', tcsh matches words beginning with "--"
# then completes the REMAINDER against LIST, so entries here must NOT
# include the leading "--" themselves (matches the find(1) example in
# `man tcsh`, e.g. 'c/-/(name newer ...)/ '), otherwise nothing matches.
set _grs_flags = (size ruling undersheet double-sided page \
    center ruling-width border-width frame-width no-frame \
    no-crop crop-gap crop-width no-label label-size output \
    help)

# Same list, but WITH the leading "--", for the 'p/*/LIST/' fallback below.
# 'c/--/LIST/' only fires once you've already typed a "-"; 'p/*/LIST/' fires
# at any position regardless of what's typed so far (including nothing),
# which is what makes TAB-on-empty list every flag.
set _grs_flags_dashed = (--size --ruling --undersheet --double-sided --page \
    --center --ruling-width --border-width --frame-width --no-frame \
    --no-crop --crop-gap --crop-width --no-label --label-size --output \
    --help)

foreach _grs_name (generate-ruling-sheet.py ./generate-ruling-sheet.py)
    complete $_grs_name \
        'n/--size/(A6 A5 B5-ISO B5-JIS B5)/' \
        'n/--ruling/(5.0 5.5 6.0 6.5 7.0 7.5 8.0 8.5 9.0 9.5)/' \
        'n/--undersheet/(right left)/' \
        'n/--page/(A6 A5 B5 A4 LETTER LEGAL)/' \
        'n/--output/f/' \
        "p/*/($_grs_flags_dashed)/"
end

unset _grs_name
#        "c/--/($_grs_flags)/" \

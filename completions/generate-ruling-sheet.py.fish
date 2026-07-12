# Fish completions for generate-ruling-sheet.py
# Install:
#   ln -s (pwd)/completions/generate-ruling-sheet.py.fish ~/.config/fish/completions/
# (fish autoloads any file in completions/ whose name matches the command's basename)

complete -c generate-ruling-sheet.py -f

complete -c generate-ruling-sheet.py -l size -x \
    -a "A6 A5 B5-ISO B5-JIS B5" \
    -d "Final trimmed paper size (default A5)"

complete -c generate-ruling-sheet.py -l ruling -x \
    -a "5.0 5.5 6.0 6.5 7.0 7.5 8.0 8.5 9.0 9.5" \
    -d "Ruling spacing in mm (default 7.0)"

complete -c generate-ruling-sheet.py -l undersheet -x \
    -a "right left" \
    -d "Wide-margin side (ignored with --double-sided)"

complete -c generate-ruling-sheet.py -l double-sided \
    -d "2-page duplex PDF, long-edge binding"

complete -c generate-ruling-sheet.py -l page -x \
    -a "A6 A5 B5 A4 LETTER LEGAL" \
    -d "Physical sheet you print on (default LETTER)"

complete -c generate-ruling-sheet.py -l center \
    -d "Center the real estate instead of flush"

complete -c generate-ruling-sheet.py -l ruling-width -x \
    -d "Ruling line width in points (default 0.6)"

complete -c generate-ruling-sheet.py -l border-width -x \
    -d "Writing-area border width in points (default 1.2)"

complete -c generate-ruling-sheet.py -l frame-width -x \
    -d "Real-estate outline width in points (default 0.5)"

complete -c generate-ruling-sheet.py -l no-frame \
    -d "Do not draw the real-estate outline"

complete -c generate-ruling-sheet.py -l no-crop \
    -d "Do not draw crop/trim marks"

complete -c generate-ruling-sheet.py -l crop-gap -x \
    -d "Gap between trim corner and crop mark in mm (default 1.5)"

complete -c generate-ruling-sheet.py -l crop-width -x \
    -d "Crop mark line width in points (default 0.5)"

complete -c generate-ruling-sheet.py -l no-label \
    -d "Do not print the size/ruling label"

complete -c generate-ruling-sheet.py -l label-size -x \
    -d "Label font size in points (default 8.0)"

complete -c generate-ruling-sheet.py -l output -r -F \
    -d "Output PDF filename"

complete -c generate-ruling-sheet.py -s h -l help \
    -d "Show help and exit"

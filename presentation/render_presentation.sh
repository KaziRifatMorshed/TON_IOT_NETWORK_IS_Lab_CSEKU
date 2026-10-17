#!/usr/bin/env bash
# ==============================================================================
# Helper Script to Render & Present TON_IoT Manim Slides
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

ACTION="${1:-html}"
# The high-quality preset creates large intermediate animations. Manim Slides
# also builds reversed copies while assembling the deck, so keep the default
# bounded for machines with limited RAM. Pass a quality explicitly to override.
QUALITY="${2:-qh}"
QUALITY_DIR="$QUALITY"
case "$QUALITY" in
    ql) QUALITY_DIR="480p15" ;;
    qm) QUALITY_DIR="720p30" ;;
    qh) QUALITY_DIR="1080p60" ;;
    qk) QUALITY_DIR="2160p60" ;;
esac

case "$ACTION" in
    render)
        echo "[INFO] Rendering TonIoTPresentation with quality -$QUALITY..."
        conda run --no-capture-output -n manim_env manim "-$QUALITY" presentation_slides.py TonIoTPresentation
        echo "[SUCCESS] Rendered video: media/videos/presentation_slides/$QUALITY_DIR/TonIoTPresentation.mp4"
        ;;
    html)
        echo "[INFO] Rendering with the memory-friendly quality preset (-$QUALITY) and converting to Reveal.js HTML..."
        conda run --no-capture-output -n manim_env manim "-$QUALITY" presentation_slides.py TonIoTPresentation
        mkdir -p ../docs
        conda run --no-capture-output -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white
        echo "[SUCCESS] Generated docs/index.html (GitHub Pages)"
        echo "Local View : file://$(cd .. && pwd)/docs/index.html"
        ;;
    present)
        echo "[INFO] Launching interactive fullscreen presentation..."
        conda run --no-capture-output -n manim_env manim-slides TonIoTPresentation
        ;;
    full-hd|1080p)
        echo "[INFO] Rendering in Full-HD (1080p60) and generating HTML..."
        conda run --no-capture-output -n manim_env manim -qh presentation_slides.py TonIoTPresentation
        mkdir -p ../docs
        conda run --no-capture-output -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white
        echo "[SUCCESS] Full-HD 1080p60 presentation exported to ../docs/index.html"
        echo "[INFO] Video: media/videos/presentation_slides/1080p60/TonIoTPresentation.mp4"
        ;;
    4k)
        echo "[INFO] Rendering in Ultra-HD 4K (2160p60, 3840x2160) for large smart boards..."
        conda run --no-capture-output -n manim_env manim -qk presentation_slides.py TonIoTPresentation
        mkdir -p ../docs
        conda run --no-capture-output -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white
        echo "[SUCCESS] Ultra-HD 4K presentation exported to docs/index.html"
        ;;
    *)
        echo "Usage: ./render_presentation.sh [html | render | 1080p | full-hd | 4k | present]"
        echo "  html    : Render slides at low memory use and generate docs/index.html (default; quality override: ./render_presentation.sh html qh)"
        echo "  full-hd : Explicit 1080p60 Full-HD render and export"
        echo "  1080p   : Alias for full-hd (1080p60 render and HTML export)"
        echo "  4k      : Render in Ultra-HD 4K (3840x2160 @ 60FPS) for 100-inch smart boards"
        echo "  present : Launch interactive local presentation window (Space to advance)"
        echo "  render  : Render video segments only without converting to HTML"
        exit 1
        ;;
esac

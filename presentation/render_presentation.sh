#!/usr/bin/env bash
# ==============================================================================
# Helper Script to Render & Present TON_IoT Manim Slides
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

ACTION="${1:-html}"
QUALITY="${2:-qh}"

case "$ACTION" in
    render)
        echo "[INFO] Rendering TonIoTPresentation with quality -$QUALITY..."
        conda run -n manim_env manim "-$QUALITY" presentation_slides.py TonIoTPresentation
        ;;
    html)
        echo "[INFO] Rendering in Full-HD (1080p60) and converting to Reveal.js HTML..."
        conda run -n manim_env manim "-$QUALITY" presentation_slides.py TonIoTPresentation
        mkdir -p ../docs
        conda run -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white
        echo "[SUCCESS] Generated high-definition docs/index.html (GitHub Pages)"
        echo "Local View : file://$(cd .. && pwd)/docs/index.html"
        ;;
    present)
        echo "[INFO] Launching interactive fullscreen presentation..."
        conda run -n manim_env manim-slides TonIoTPresentation
        ;;
    full-hd)
        echo "[INFO] Rendering in Full-HD (1080p60) and generating HTML..."
        conda run -n manim_env manim -qh presentation_slides.py TonIoTPresentation
        mkdir -p ../docs
        conda run -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white
        echo "[SUCCESS] Full-HD 1080p60 presentation exported to docs/index.html"
        ;;
    4k)
        echo "[INFO] Rendering in Ultra-HD 4K (2160p60, 3840x2160) for large smart boards..."
        conda run -n manim_env manim -qk presentation_slides.py TonIoTPresentation
        mkdir -p ../docs
        conda run -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white
        echo "[SUCCESS] Ultra-HD 4K presentation exported to docs/index.html"
        ;;
    *)
        echo "Usage: ./render_presentation.sh [html | full-hd | 4k | present | render]"
        echo "  html    : Render slides in 1080p60 and generate standalone docs/index.html (default)"
        echo "  full-hd : Explicit 1080p60 Full-HD render and export"
        echo "  4k      : Render in Ultra-HD 4K (3840x2160 @ 60FPS) for 100-inch smart boards"
        echo "  present : Launch interactive local presentation window (Space to advance)"
        echo "  render  : Render video segments only without converting to HTML"
        exit 1
        ;;
esac

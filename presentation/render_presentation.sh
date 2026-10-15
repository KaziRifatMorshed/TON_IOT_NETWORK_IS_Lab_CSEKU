#!/usr/bin/env bash
# ==============================================================================
# Helper Script to Render & Present TON_IoT Manim Slides
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

ACTION="${1:-html}"
QUALITY="${2:-ql}"

case "$ACTION" in
    render)
        echo "[INFO] Rendering TonIoTPresentation with quality -$QUALITY..."
        conda run -n manim_env manim "-$QUALITY" presentation_slides.py TonIoTPresentation
        ;;
    html)
        echo "[INFO] Rendering and converting to Reveal.js HTML..."
        conda run -n manim_env manim "-$QUALITY" presentation_slides.py TonIoTPresentation
        conda run -n manim_env manim-slides convert TonIoTPresentation ton_iot_presentation.html -c reveal_theme=white
        mkdir -p ../docs
        conda run -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white
        echo "[SUCCESS] Generated presentation/ton_iot_presentation.html and docs/index.html (GitHub Pages)"
        echo "Local View : file://$DIR/ton_iot_presentation.html"
        echo "GitHub Page: file://$(cd .. && pwd)/docs/index.html"
        ;;
    present)
        echo "[INFO] Launching interactive fullscreen presentation..."
        conda run -n manim_env manim-slides TonIoTPresentation
        ;;
    full-hd)
        echo "[INFO] Rendering in Full-HD (1080p60) and generating HTML..."
        conda run -n manim_env manim -qh presentation_slides.py TonIoTPresentation
        conda run -n manim_env manim-slides convert TonIoTPresentation ton_iot_presentation.html -c reveal_theme=white
        mkdir -p ../docs
        conda run -n manim_env manim-slides convert TonIoTPresentation ../docs/index.html --one-file -c reveal_theme=white
        echo "[SUCCESS] Full-HD presentation rendered and exported to ton_iot_presentation.html and docs/index.html"
        ;;
    *)
        echo "Usage: ./render_presentation.sh [html | render | present | full-hd]"
        echo "  html    : Render slides (quick) and generate ton_iot_presentation.html (default)"
        echo "  full-hd : Render in 1080p60 and generate ton_iot_presentation.html"
        echo "  present : Launch interactive presentation window (Space to advance)"
        echo "  render  : Render video segments only"
        exit 1
        ;;
esac

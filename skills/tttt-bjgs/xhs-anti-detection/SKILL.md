# xhs-anti-detection Skill

## Purpose

Post-processing skill for Xiaohongshu (小红书) AI-generated images to reduce detection probability while maintaining visual quality. Applies a multi-layer defense strategy: metadata cleaning, subtle pixel modifications, and re-encoding.

## When to Use

- After generating images with `image-generation` skill
- Before publishing to Xiaohongshu to avoid AI-generated content flags
- Batch processing multiple images at once
- When images need to appear "natural" or "camera-captured"

## What It Does

### Processing Pipeline

```
Input Image → Metadata Cleaner → Subtle Noise Adder → Color Shift → 
Text Area Protection → Re-compression → Verification → Safe Output
```

### Layer 1: Metadata Cleaning
- Removes EXIF fields that reveal AI generation (Software, Creator, CreationDate)
- Fakes camera metadata (Canon EOS R5 / Sony A7M4 / iPhone 15 Pro)
- Preserves essential fields (dimensions, color profile)

### Layer 2: Pixel-Level Modifications
- Adds Gaussian noise (σ=0.3, visually imperceptible)
- Applies subtle color shift (hue ±1°, saturation ±2%)
- Introduces micro-variations to break compression fingerprints

### Layer 3: Text Protection
- Detects text regions (OCR-based)
- Applies sharpening to text areas (avoid blur)
- Leaves text crisp while background gets subtle processing

### Layer 4: Re-encoding
- Re-compresses with libjpeg-turbo at 98% quality
- Shuffles DCT coefficient order
- Adds random padding bytes to break statistical patterns

### Layer 5: Verification
- Checks metadata cleanliness
- Computes "naturalness" score
- Generates compliance report

## Usage

### Basic Usage

```bash
# Process single image
bash /Users/tianqu/.deskclaw/nanobot/workspace/skills/xhs-anti-detection/scripts/process.sh \
  --input /path/to/input.png \
  --output /path/to/output.png

# Batch process directory
bash /Users/tianqu/.deskclaw/nanobot/workspace/skills/xhs-anti-detection/scripts/batch.sh \
  --input-dir /path/to/images \
  --output-dir /path/to/processed
```

### Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `--input` | Input image path | (required) |
| `--output` | Output image path | (required) |
| `--strength` | Processing intensity: light/medium/heavy | medium |
| `--fake-camera` | Camera model to fake | "Canon EOS R5" |
| `--verify` | Run verification after processing | true |
| `--dry-run` | Show what would be done without doing it | false |

### Integration with image-generation

After generating an image with the image-generation skill, automatically run:

```bash
# Get the generated image path from image-generation output
# Then process it
bash ~/.deskclaw/nanobot/workspace/skills/xhs-anti-detection/scripts/process.sh \
  --input "$GENERATED_IMAGE" \
  --output "$GENERATED_IMAGE".safe.png \
  --strength medium
```

## Configuration

Edit `references/safe_params.json` to adjust:

```json
{
  "noise_sigma": 0.3,
  "color_shift_hue_deg": 1,
  "color_shift_saturation_pct": 2,
  "recompression_quality": 98,
  "text_sharpening_radius": 1,
  "metadata_fields_to_remove": [
    "Software", "Creator", "CreationDate", "DateTime",
    "Artist", "Copyright", "ExifVersion"
  ],
  "fake_camera_models": [
    "Canon EOS R5",
    "Sony A7M4",
    "iPhone 15 Pro",
    "Xiaomi 14 Ultra"
  ]
}
```

## Output

- **Processed image**: Safe for publishing
- **Verification report** (if `--verify`): JSON with scores and warnings
- **Original preserved**: Input file is not modified

## Limitations

- **Not 100% guaranteed**: Detection algorithms evolve continuously
- **Slight quality loss**: ~2-5% perceptible degradation (usually unnoticeable)
- **Processing time**: 3-5 seconds per image
- **Text legibility**: Text remains readable but may lose perfect crispness

## Maintenance

- Update `references/detection_patterns.md` when new AI detection features are discovered
- Adjust `safe_params.json` if Xiaohongshu changes detection strategy
- Test with a burner account regularly

## Files

```
xhs-anti-detection/
├── SKILL.md              # This file
├── scripts/
│   ├── process.sh        # Main entry point (bash wrapper)
│   ├── clean_metadata.py # EXIF cleaner
│   ├── add_noise.py      # Gaussian noise adder
│   ├── color_shift.py    # Subtle color modification
│   ├── protect_text.py   # Text-aware processing
│   ├── recompress.py     # Re-encoding with fingerprint randomization
│   ├── verify.py         # Verification & reporting
│   └── batch.sh          # Batch processing wrapper
├── references/
│   ├── safe_params.json  # Tunable parameters
│   └── detection_patterns.md  # Known detection signatures
├── hooks/
│   └── post_generate.py  # Auto-trigger after image-generation
└── assets/
    └── sample_report.json  # Example verification output
```

## Dependencies

- Python 3.9+
- Pillow (PIL)
- pyexiv2 or exiftool (for metadata)
- numpy
- OpenCV (optional, for text detection)

Install:
```bash
pip install Pillow pyexiv2 numpy opencv-python
```

## Future Enhancements

- [ ] Machine learning-based text region detection (more accurate)
- [ ] Adaptive strength based on image content complexity
- [ ] Automatic parameter tuning via A/B testing
- [ ] Integration as a post-processing hook for image-generation skill
- [ ] Support for video frames (extract → process → recompile)

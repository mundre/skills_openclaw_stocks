# Prompt Cookbook

Proven prompt patterns for pixcli. Copy-paste and adapt.

## Image generation

### Product photography
```bash
pixcli image "Studio product shot of [PRODUCT], soft directional lighting, \
  white cyclorama background, shallow depth of field, 85mm lens look" -r 16:9 -q high
```

### SaaS dashboard UI
```bash
pixcli image "Clean SaaS analytics dashboard, dark mode, \
  data visualization with blue and purple accent colors, glassmorphism cards, \
  no text placeholders, professional UI design" -r 16:9
```

### Lifestyle context shot
```bash
pixcli image "Professional woman using [PRODUCT] at a modern coworking space, \
  natural window light, candid moment, editorial photography style"
```

### Isometric illustration
```bash
pixcli image "Isometric 3D render of [SCENE], miniature style, \
  warm indirect lighting, pastel color palette, clean white background" -q high
```

### Transparent asset for compositing
```bash
pixcli image "[OBJECT] centered, clean edges, product photography lighting" -t -o asset.png
```

### Icon / asset with green screen trick
```bash
pixcli image "[OBJECT] centered on a solid bright green background (#00FF00), \
  no shadows, no gradients, flat green, product photography lighting" -o raw.png
# Then remove the green:
pixcli edit "Remove the background" -i raw.png -o clean.png
```

### Multiple variations for selection
```bash
pixcli image "Abstract geometric pattern, tech vibes, dark blue and cyan" -n 4
```

### Hero shot (maximum quality)
```bash
pixcli image "Luxury tech product floating in volumetric light, \
  photorealistic, dramatic studio lighting, 8K detail" -q high -o hero.png
```

### Consistent visual kit (same style across scenes)
```bash
# Use shared style cues in every prompt for visual consistency
pixcli image "Scene 1: [DESCRIPTION], flat illustration style, \
  blue and orange palette, thick outlines" -o scene-1.png
pixcli image "Scene 2: [DESCRIPTION], flat illustration style, \
  blue and orange palette, thick outlines" -o scene-2.png
pixcli image "Scene 3: [DESCRIPTION], flat illustration style, \
  blue and orange palette, thick outlines" -o scene-3.png
```

### Multi-image reference generation
```bash
# Combine multiple reference images into a new creation
pixcli image "combine these into a product collage" --from shot1.png --from shot2.png
```

### Search grounding for real-world accuracy
```bash
# Use --search for correct logos, brands, current events
pixcli image "latest iPhone 16 Pro on a desk" --search

# Real brand accuracy
pixcli image "Nike Air Max 90 product shot on white background" --search -q high
```

### Specific model for best results
```bash
# Nano Banana Pro — best text rendering and consistency
pixcli image "Tech startup logo with the text 'FLOWPILOT'" -m nano-banana-pro -o logo.png

# Imagen 4 — highest quality photorealism
pixcli image "Ultra-realistic portrait, golden hour" -m imagen-4 -o portrait.png

# FLUX 2 Pro — strong general-purpose generation
pixcli image "Futuristic cityscape at night" -m flux-pro -o city.png
```

## Image editing

### Upscale for final delivery
```bash
pixcli edit "Upscale to maximum resolution, preserve all details" -i hero.png -q high -o hero-4k.png
```

### Remove background for Remotion compositing
```bash
pixcli edit "Remove the background" -i product.jpg -o product-nobg.png
```

### Enhance and improve quality
```bash
pixcli edit "Enhance image quality, sharpen details, improve colors" -i photo.jpg -o enhanced.jpg
```

### Style transfer from a reference
```bash
pixcli edit "Apply the artistic style from the second image to the first" \
  -i photo.jpg -i artistic-ref.jpg -o stylized.png
```

### Multi-image composition
```bash
pixcli edit "Combine these product shots into a clean collage layout" \
  -i shot1.png -i shot2.png -i shot3.png -o collage.png
```

### Specific edit model
```bash
# Background removal
pixcli edit "Remove background" -i product.jpg -m rembg -o nobg.png

# High-quality upscale
pixcli edit "Upscale 4x" -i photo.png -m recraft-upscale -o upscaled.png

# Enhancement
pixcli edit "Enhance and clean up" -i raw.jpg -m phota-enhance -o enhanced.jpg
```

## Prompt writing tips

### Be specific about style
- Include lighting: "soft directional", "dramatic rim lighting", "natural window light"
- Include lens: "85mm lens look", "wide angle", "macro close-up"
- Include mood: "warm and inviting", "cold and clinical", "energetic and bold"

### For product shots
- Mention the surface: "white cyclorama", "dark reflective surface", "marble countertop"
- Mention depth of field: "shallow depth of field", "everything in focus"
- Mention angle: "45-degree hero angle", "straight-on", "bird's eye view"

### For consistency across images
- Lock style keywords and reuse them across all prompts
- Keep color palette explicit: "blue and orange palette" not just "colorful"
- Keep character/product descriptions identical across scenes

### For editing
- Be explicit about what to change: "Remove the background" not "Clean up the image"
- For style transfer, describe what aspects to transfer: "color palette and brushstroke style"
- For upscaling, mention what matters: "preserve text clarity" or "maintain sharp edges"

## Video generation

> **Formula**: Subject → Action → Environment → Camera → Style → Constraints. Target 60–100 words. One camera move per shot. See `seedance-playbook.md` for the full masterclass.

### Text-to-video using the 6-element formula
```bash
pixcli video "A woman in her 30s, short black hair, red wool coat, walks briskly through a rain-slicked Tokyo street at night. Neon signs reflect on wet pavement. She glances over her shoulder. Slow push-in. Cinematic, shallow depth of field, film grain, cool blue palette. Smooth motion, stable framing." \
  -d 8 -r 16:9 -q high -o tokyo.mp4
```

### Seedance auto-routing via keyword
```bash
# Any of these prompts route to Seedance on muapi automatically
# (no -m flag needed): "seedance", "bytedance", "doubao" in the text
pixcli video "Seedance cinematic style: a bartender slides a cocktail across a polished bar, ice clinks, amber liquid catches the neon light, camera tracks the glass, moody jazz club, warm tones, shallow DOF." \
  -d 8 -r 16:9 -q high -o cocktail.mp4
```

### Seedance explicit product hero (orbit)
```bash
pixcli video "A sleek titanium laptop sits open on a marble desk in a minimalist studio. Morning light streams through floor-to-ceiling windows. Camera orbits slowly around the product, 90 degrees. Clean, ultra-sharp, 4K detail, neutral warm palette. Smooth orbit, no jitter." \
  -m seedance-2-t2v -d 10 -r 16:9 -q high -o product-hero.mp4
```

### Seedance I2V — portrait come to life
```bash
# Describe ONLY the motion. The image carries composition and identity.
pixcli video "She slowly turns her head toward camera, a subtle smile forming. Eyes blink naturally. Hair moves gently in a light breeze. Camera holds fixed. Soft natural window light. Preserve composition and colors." \
  --from portrait.png -m seedance-2-i2v -d 5 -r 9:16 -q high -o portrait-alive.mp4
```

### Seedance first-frame → last-frame transition
```bash
pixcli video "Character leaps upward with explosive energy, arms raised, reaching maximum height at the final frame. Natural motion arc. Preserve character appearance." \
  --from standing.png --to jumping.png \
  -m seedance-2-first-last-frame -d 5 -r 16:9 -o leap.mp4
```

### Seedance video extend (new seconds only)
```bash
# -d is the NEW seconds to add, not the total.
pixcli video "Camera tilts upward as the neon sign flickers on. Steam rises from the coffee cup. The door opens. Warm street light spills into the room." \
  --from scene.mp4 --extend -m seedance-2-extend -d 6 -o scene-extended.mp4
```

### Seedance video edit (change identity, keep motion)
```bash
pixcli video "Keep the original motion and camera work. Change the character's hair to long red hair. Add fog rolling through the background." \
  --from original.mp4 -m seedance-2-video-edit -d 5 -o edited.mp4
```

### Draft iteration loop (auto-routes to 480p Seedance)
```bash
# --quality draft triggers the 480p Seedance tier — ~6x cheaper.
# Validate composition + motion before committing to a full render.
pixcli video "Woman walking through rain, neon reflections, slow push-in, cinematic" \
  -d 5 -q draft -o test.mp4
```

### Timeline prompt for a 12s brand story
```bash
pixcli video "[Global: warm cinematic, shallow DOF, golden tones, documentary] \
[0s-3s]: Wide shot, static. Small bakery at dawn, flour dust in morning light, empty tables. \
[3s-7s]: Medium shot, slow push-in. Baker in white apron shapes dough with practiced hands. \
[7s-11s]: Close-up, fixed. Hands pressing dough. Texture detail. Quiet focus. \
[11s-12s]: Wide shot, slow dolly out. Full bakery revealed, warm and alive." \
  -m seedance-2-t2v -d 12 -r 16:9 -q high -o bakery-story.mp4
```

### Negative prompt for artifact-prone shots
```bash
pixcli video "A dancer spins on a spotlit stage. Camera holds fixed. Dramatic stage lighting, black background." \
  --negative "jitter, morphing, warped faces, duplicate limbs, unstable framing, jump cuts, text artifacts" \
  -m seedance-2-t2v -d 6 -r 9:16 -q high -o dancer.mp4
```

### Hero product reveal (image first, then animate)
```bash
# Generate the hero still
pixcli image "Luxury headphones floating in volumetric light, dark background, \
  dramatic studio lighting" -q high -o hero.png

# Animate it into a short clip
pixcli video "Slow camera orbit revealing the product, volumetric light rays shift" \
  --from hero.png -d 5 -q high -o hero-clip.mp4
```

### Cinematic B-roll
```bash
pixcli video "Aerial drone shot of modern city skyline at golden hour, \
  slow dolly forward, cinematic color grading" -r 16:9 -d 8 -q high -o broll-city.mp4
```

### App demo animation
```bash
# Start from a UI screenshot
pixcli video "User scrolls through the dashboard, cursor clicks the analytics tab, \
  smooth transition to chart view" --from app-screenshot.png -d 6 -o app-demo.mp4
```

### Video with start and end frames (transition)
```bash
# Smooth morph between two images
pixcli video "smooth morph" --from scene1.png --to scene2.png

# Day-to-night transition with PixVerse
pixcli video "transform from day to night" --from day.png --to night.png -m pixverse-v6-transition
```

### Video with native audio
```bash
# Generate video with built-in audio (BGM, SFX, dialogue)
pixcli video "dramatic reveal" --from product.png --audio

# PixVerse v6 with audio
pixcli video "energetic product showcase with upbeat music" --from hero.png --audio -m pixverse-v6-i2v
```

### Extending a video clip
```bash
# Add 5 more seconds to an existing clip
pixcli video "Continue the camera movement, maintain consistent lighting and pace" \
  --from hero-clip.mp4 --extend -d 5 -o hero-extended.mp4
```

## Audio

### Professional voiceover
```bash
pixcli voice "Introducing FlowPilot — the productivity platform that actually gets out of your way." \
  --voice Rachel -o vo-intro.mp3
```

### Background music (ducks under VO)
```bash
pixcli music "Upbeat corporate background, light piano and soft synth pads, \
  positive energy, not overpowering" -d 45 -o music-bg.mp3
```

### Transition whoosh SFX
```bash
pixcli sfx "Smooth cinematic whoosh transition, left to right" -d 1 -o whoosh.mp3
```

### UI click sound SFX
```bash
pixcli sfx "Soft digital UI button click, subtle and satisfying" -d 0.5 -o click.mp3
```

## Job recovery

### Recover a timed-out video job
```bash
# Video generation timed out — use the job ID from the error message
pixcli job abc123def --wait -o hero-clip.mp4

# Check status without waiting
pixcli job abc123def --json
```

const fs = require('fs');
const { createCanvas } = require('canvas');

/**
 * QR-Renderer: Converts ASCII QR code matrices (█, ▀, ▄, space) into high-definition PNGs.
 * Useful for headless server environments where terminal output cannot be easily scanned.
 */
function renderQR(inputPath, outputPath) {
    const rawData = fs.readFileSync(inputPath, 'utf8');
    const lines = rawData.split('\n').filter(line => line.trim().length > 0);
    
    // Auto-detect matrix dimensions
    const height = lines.length;
    const width = Math.max(...lines.map(l => l.length));
    
    // Scale factor: each block character is represented as a 10x10 (or 10x20) pixel block
    const scale = 10;
    const canvas = createCanvas(width * scale, height * scale * 2); 
    const ctx = canvas.getContext('2d');

    // Background: White
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Drawing pixels: Black
    ctx.fillStyle = '#000000';
    lines.forEach((line, y) => {
        for (let x = 0; x < line.length; x++) {
            const char = line[x];
            // █: Full Black
            if (char === '█') {
                ctx.fillRect(x * scale, y * scale * 2, scale, scale * 2);
            } 
            // ▀: Upper Half Block
            else if (char === '▀') {
                ctx.fillRect(x * scale, y * scale * 2, scale, scale);
            } 
            // ▄: Lower Half Block
            else if (char === '▄') {
                ctx.fillRect(x * scale, y * scale * 2 + scale, scale, scale);
            }
        }
    });

    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(outputPath, buffer);
    console.log(`[QR-Renderer] HD QR Code generated at: ${outputPath}`);
}

const args = process.argv.slice(2);
if (args.length < 2) {
    console.log("Usage: node qr_renderer.js <input_txt> <output_png>");
    process.exit(1);
}

renderQR(args[0], args[1]);

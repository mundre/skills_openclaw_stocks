# Product Image Enrichment

How to find product images when creating receipts. Merchant logos are handled automatically by the backend — you only need to provide product images.

## Where to find product images

In priority order:

1. **`og:image` meta tag on the product page.** This is the most reliable source. Almost all e-commerce sites set `og:image` on product pages with a high-quality product photo (typically 1200x630 or larger). You are already visiting the product page in step 1 of the purchase workflow — grab the `og:image` URL at that point.

2. **Main product image on the page.** If `og:image` is not available, look for the primary product image in the product detail area. It is usually the largest image on the page, often inside a container with a class like `product-image`, `product-media`, or similar.

3. **Checkout thumbnail.** Some checkout flows display a small thumbnail of the item. This works as a last resort but is often low-resolution.

## When to capture the image URL

Capture the product image URL early — when you first visit the product page in step 1 (Confirm the purchase details). Store it for later use in `create_receipt`.

Do not wait until checkout to look for images. Checkout pages often show only tiny thumbnails, and some omit images entirely.

## Image quality guidelines

- Prefer images over 200px on the longest side
- Use HTTPS URLs only
- Prefer direct image URLs (ending in `.jpg`, `.png`, `.webp`) over page URLs
- Do not use `data:` URIs or base64-encoded images
- If no suitable image is found, omit the field — a missing image is better than a broken one

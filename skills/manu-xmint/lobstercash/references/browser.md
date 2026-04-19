# Browser — Cloud Browser Automation

Control a cloud browser session for browsing websites, product discovery, and completing checkout. The browser runs server-side; the user can watch live via a shareable URL.

## Key concepts

- **Session per agent:** Each agent has one active browser session at a time. Opening a new session replaces the previous one.
- **Server-side credentials:** The `fill-card` command reveals and fills card credentials entirely on the server. Card numbers and CVCs never reach the agent or CLI.
- **Live view:** Every session has a live view URL the user can open to watch the browser in real time.
- **Natural language:** The `act` command accepts plain-English instructions (e.g. "click add to cart", "scroll down", "select size Large").

---

## Commands

### `browser open`

Start a browser session and navigate to a URL.

```bash
lobstercash browser open <url>
```

#### Output

- `Live view:` — shareable URL where the user can watch the session
- `Page:` — page title after navigation
- `URL:` — final URL (may differ from input after redirects)
- `Session:` — session ID (stored automatically)
- `Screenshot:` — URL to a screenshot of the loaded page

#### After running

Share the live view URL with the user:

> I've opened the page. You can watch along here:
>
> [Live view URL]

#### When to use

- Starting a shopping flow ("find me socks on nike.com")
- Navigating to a merchant's checkout page
- Browsing any website the user asks about

---

### `browser act`

Perform a natural-language action in the browser.

```bash
lobstercash browser act "<instruction>"
```

#### Examples

```bash
lobstercash browser act "click add to cart"
lobstercash browser act "select size Large from the dropdown"
lobstercash browser act "scroll down to see more products"
lobstercash browser act "go to checkout"
lobstercash browser act "fill in the email field with user@example.com"
```

#### Output

- `Result:` — summary of what happened
- `Screenshot:` — URL to a screenshot after the action

#### When to use

- Clicking buttons, links, dropdowns
- Filling non-sensitive form fields (shipping address, email, name)
- Navigating between pages
- Any interaction you'd describe to a human

#### What NOT to do

- Do not use `act` to fill card credentials — use `fill-card` instead
- Do not click "place order" or "submit payment" without asking the user first

---

### `browser extract`

Extract structured data from the current page.

```bash
lobstercash browser extract "<query>"
```

#### Examples

```bash
lobstercash browser extract "all product names, prices, and URLs on this page"
lobstercash browser extract "the order total and shipping cost"
lobstercash browser extract "available sizes and colors for this product"
```

#### Output

JSON-formatted extracted data.

#### When to use

- Product discovery (browsing a catalog, comparing prices)
- Reading order summaries before confirming
- Scraping specific information the user asked about

---

### `browser observe`

List actionable elements on the current page.

```bash
lobstercash browser observe
```

#### Output

A numbered list of interactive elements with descriptions and suggested actions:

```
1. "Add to Cart" button → click
2. Size dropdown → select
3. Search input → type
```

#### When to use

- Understanding what's possible on the current page
- Debugging when `act` can't find an element
- Orienting after navigation to a new page

---

### `browser screenshot`

Take a screenshot of the current page.

```bash
lobstercash browser screenshot
```

#### Output

- `Page:` — page title
- `URL:` — current URL
- `Screenshot:` — URL to the screenshot

#### When to use

- Showing the user what the page looks like before a critical action (e.g. before placing an order)
- Confirming an action was performed correctly
- Any time you need visual context

---

### `browser fill-card`

Reveal virtual card credentials on the server and fill the payment form in the browser. Card credentials are handled entirely server-side and never reach the CLI or agent.

```bash
lobstercash browser fill-card \
  --card-id <orderIntentId> \
  --merchant-name "<merchant name>" \
  --merchant-url "https://merchant.com" \
  --merchant-country <XX>
```

#### Flags

- `--card-id` — the card's `orderIntentId` (from `lobstercash cards list`)
- `--merchant-name` — real merchant name
- `--merchant-url` — canonical merchant URL
- `--merchant-country` — ISO 3166-1 alpha-2 country code (e.g. `US`, `GB`)

#### Output

- `Payment form filled (card ending XXXX).`
- `Card credentials were handled server-side and never reached this device.`

#### When to use

- At the payment step of checkout, after the browser has navigated to the payment form
- Only for cards in `active` phase (check with `lobstercash cards list`)

#### What NOT to do

- Do not use `cards reveal` + `browser act` to fill card details — that would send credentials through the LLM. Always use `fill-card`.
- Do not call this before the checkout page is showing a payment form

---

### `browser close`

Close the active browser session and release resources.

```bash
lobstercash browser close
```

#### Output

- `Browser session closed for agent "<agentId>".`

#### When to use

- After checkout is complete
- When the user is done browsing
- Before opening a different site (a new `browser open` also replaces the session)

---

## End-to-end checkout example

```bash
# 1. Open the merchant site
lobstercash browser open "https://store.example.com/socks"

# 2. Browse and select a product
lobstercash browser extract "product names, prices, and links"
lobstercash browser act "click on the 'Athletic Crew Socks' product"
lobstercash browser act "select size Large"
lobstercash browser act "click add to cart"
lobstercash browser act "go to checkout"

# 3. Fill shipping info
lobstercash browser act "fill shipping name with 'Jane Doe'"
lobstercash browser act "fill shipping address with '123 Main St, Springfield, IL 62701'"

# 4. Fill payment (credentials stay server-side)
lobstercash browser fill-card \
  --card-id abc123 \
  --merchant-name "Example Store" \
  --merchant-url "https://store.example.com" \
  --merchant-country US

# 5. Review before placing order
lobstercash browser screenshot
# → Show screenshot to user, ask "Does this look right? Should I place the order?"

# 6. Place the order (only after user confirms)
lobstercash browser act "click place order"

# 7. Clean up
lobstercash browser close
```

## Gotchas

- **Requires an active agent:** All browser commands use the active agent's session. Run `lobstercash agents list` first.
- **One session per agent:** Opening a new URL replaces any existing session for that agent.
- **Sessions time out:** Browser sessions are cloud-hosted and will eventually expire if idle. If a session times out, `open` a new one.
- **Not all sites work:** Some sites with aggressive bot detection may block automated browsers. If a site isn't working, tell the user and suggest they complete checkout manually with `cards reveal` instead.

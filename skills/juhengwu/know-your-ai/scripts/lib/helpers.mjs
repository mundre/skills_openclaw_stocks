/**
 * Know Your AI — Shared helpers for skill scripts
 */

/**
 * Parse a Know Your AI DSN string into its components.
 * Format: https://kya_xxx:da2-xxx@host/product_id
 */
export function parseDsn(dsn) {
  const url = new URL(dsn);
  const apiKey = url.username;
  const authToken = decodeURIComponent(url.password);
  const host = url.hostname + (url.port ? `:${url.port}` : "");
  const productId = url.pathname.replace(/^\//, "").replace(/\/$/, "");
  if (!apiKey || !authToken || !host || !productId) {
    throw new Error("DSN must contain api_key, auth_token, host, and product_id");
  }
  return { apiKey, authToken, host, productId };
}

/**
 * Execute a GraphQL query against the Know Your AI API.
 */
export async function gql(parsed, query, variables) {
  const resp = await fetch(`https://${parsed.host}/graphql`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: parsed.authToken,
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`API request failed (${resp.status}): ${text.slice(0, 300)}`);
  }

  const data = await resp.json();
  if (data.errors) {
    throw new Error(`GraphQL errors: ${JSON.stringify(data.errors).slice(0, 300)}`);
  }
  return data;
}

/**
 * Format an error for display.
 */
export function formatError(err) {
  return err instanceof Error ? err.message : String(err);
}

#!/usr/bin/env node

/**
 * Know Your AI — List evaluations and datasets
 */

import { parseDsn, gql, formatError } from "./lib/helpers.mjs";

const dsn = (process.env.KNOW_YOUR_AI_DSN ?? "").trim();
if (!dsn) {
  console.error("✖ Missing KNOW_YOUR_AI_DSN. Set it via: export KNOW_YOUR_AI_DSN=...");
  process.exit(1);
}

const parsed = parseDsn(dsn);

try {
  // Fetch evaluations
  const evalQuery = `
    query ListEvaluations {
      listEvaluations(filter: { productID: { eq: "${parsed.productId}" } }, limit: 50) {
        items {
          id
          name
          judgeModel
          threshold
          createdAt
        }
      }
    }
  `;

  const evalData = await gql(parsed, evalQuery);
  const evaluations = evalData?.data?.listEvaluations?.items ?? [];

  console.log("## Evaluations\n");
  if (evaluations.length === 0) {
    console.log("  (none found)\n");
  } else {
    for (const ev of evaluations) {
      const threshold = ev.threshold != null ? ` | threshold: ${ev.threshold}` : "";
      const judge = ev.judgeModel ? ` | judge: ${ev.judgeModel}` : "";
      console.log(`- **${ev.name || "(unnamed)"}**`);
      console.log(`  ID: ${ev.id}${judge}${threshold}`);
    }
  }

  // Fetch datasets
  const dsQuery = `
    query ListDatasets {
      listDatasets(filter: { productID: { eq: "${parsed.productId}" } }, limit: 50) {
        items {
          id
          name
          promptCount
          createdAt
        }
      }
    }
  `;

  const dsData = await gql(parsed, dsQuery);
  const datasets = dsData?.data?.listDatasets?.items ?? [];

  console.log("\n## Datasets\n");
  if (datasets.length === 0) {
    console.log("  (none found)");
  } else {
    for (const ds of datasets) {
      const count = ds.promptCount != null ? ` | ${ds.promptCount} prompts` : "";
      console.log(`- **${ds.name || "(unnamed)"}**`);
      console.log(`  ID: ${ds.id}${count}`);
    }
  }
} catch (err) {
  console.error(`✖ ${formatError(err)}`);
  process.exit(1);
}

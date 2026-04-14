import { Type } from "@sinclair/typebox";
import { execSync, execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { hexdump, fetchJson, extractStrings } from "./utils.mjs";
import { getConfig } from "./config.mjs";

export function makeNpmPackageAnalysisTool() {
  return {
    name: "npm_package_analysis",
    label: "NPM Package Analysis",
    description:
      "Fetch and summarize metadata for an npm package from the public registry. " +
      "Returns key info: version count, publish dates, maintainers, repository, etc. " +
      "Use this to investigate npm dependencies for supply-chain risk assessment.",
    parameters: Type.Object({
      package_name: Type.String({ description: "The npm package name, e.g. 'lodash' or '@scope/pkg'" }),
    }),
    execute: async (_toolCallId, params) => {
      const pkg = params.package_name;
      const npmBase = getConfig().npmRegistryUrl.replace(/\/+$/, "");
      const url = `${npmBase}/${encodeURIComponent(pkg).replace("%40", "@").replace("%2F", "/")}`;

      let data;
      try {
        data = await fetchJson(url);
      } catch (err) {
        if (err.message.includes("404")) {
          return {
            content: [{ type: "text", text: `## NPM Package Analysis: ${pkg}\n\n**Package does not exist on npm.** This is a strong supply-chain risk indicator — the dependency may be typosquatted, removed, or never published.` }],
            details: { package: pkg, exists: false },
          };
        }
        throw new Error(`Failed to fetch npm registry for "${pkg}": ${err.message}`);
      }

      // --- Extract key fields ---
      const name = data.name || pkg;
      const description = data.description || "(no description)";
      const license = data.license || "unknown";
      const homepage = data.homepage || null;
      const repoUrl = data.repository?.url || null;
      const keywords = data.keywords || [];
      const maintainers = (data.maintainers || []).map(
        (m) => `${m.name}${m.email ? ` <${m.email}>` : ""}`
      );

      // --- Version analysis ---
      const timeEntries = data.time || {};
      const versionTimes = Object.entries(timeEntries).filter(
        ([k]) => k !== "created" && k !== "modified"
      );
      versionTimes.sort((a, b) => new Date(a[1]) - new Date(b[1]));

      const totalVersions = versionTimes.length;
      const firstVersion = versionTimes[0] || null;
      const latestTag = data["dist-tags"]?.latest || null;
      const latestTime = latestTag && timeEntries[latestTag]
        ? timeEntries[latestTag]
        : versionTimes[versionTimes.length - 1]?.[1] || null;

      const firstPublishDate = firstVersion ? new Date(firstVersion[1]) : null;
      const now = new Date();
      const threeMonthsAgo = new Date(now);
      threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
      const isNewPackage = firstPublishDate && firstPublishDate > threeMonthsAgo;

      // --- Latest version details ---
      const latestVersionData = latestTag && data.versions?.[latestTag];
      const dependencies = latestVersionData?.dependencies
        ? Object.keys(latestVersionData.dependencies)
        : [];
      const devDependencies = latestVersionData?.devDependencies
        ? Object.keys(latestVersionData.devDependencies)
        : [];
      const scripts = latestVersionData?.scripts || {};
      const hasLifecycleScripts = ["preinstall", "install", "postinstall", "preuninstall", "postuninstall"].some(
        (s) => s in scripts
      );

      // --- Build text summary ---
      const lines = [];
      lines.push(`## NPM Package Analysis: ${name}`);
      lines.push("");

      if (isNewPackage) {
        lines.push(`⚠️  **WARNING: This package was first published less than 3 months ago (${firstVersion[1]}). This is a supply-chain risk indicator.**`);
        lines.push("");
      }

      lines.push(`- **Description**: ${description}`);
      lines.push(`- **License**: ${license}`);
      lines.push(`- **Total versions published**: ${totalVersions}`);
      lines.push(`- **First version**: ${firstVersion ? `${firstVersion[0]} (${firstVersion[1]})` : "unknown"}`);
      lines.push(`- **Latest version**: ${latestTag || "unknown"} (${latestTime || "unknown"})`);
      lines.push(`- **Repository**: ${repoUrl || "not specified"}`);
      if (homepage) lines.push(`- **Homepage**: ${homepage}`);
      lines.push(`- **Maintainers**: ${maintainers.length ? maintainers.join(", ") : "none listed"}`);
      if (keywords.length) lines.push(`- **Keywords**: ${keywords.join(", ")}`);

      lines.push("");
      lines.push(`### Dependencies (latest version)`);
      lines.push(`- **Runtime dependencies** (${dependencies.length}): ${dependencies.length ? dependencies.join(", ") : "none"}`);
      lines.push(`- **Dev dependencies** (${devDependencies.length}): ${devDependencies.length ? devDependencies.join(", ") : "none"}`);

      if (hasLifecycleScripts) {
        const lifecycleEntries = ["preinstall", "install", "postinstall", "preuninstall", "postuninstall"]
          .filter((s) => s in scripts)
          .map((s) => `  - ${s}: \`${scripts[s]}\``);
        lines.push("");
        lines.push(`### ⚠️  Lifecycle Scripts Detected`);
        lines.push(...lifecycleEntries);
      }

      if (Object.keys(scripts).length) {
        lines.push("");
        lines.push(`### Package Scripts`);
        for (const [k, v] of Object.entries(scripts)) {
          lines.push(`- ${k}: \`${v}\``);
        }
      }

      // --- Publish frequency analysis ---
      if (totalVersions >= 2) {
        const firstDate = new Date(versionTimes[0][1]);
        const lastDate = new Date(versionTimes[versionTimes.length - 1][1]);
        const spanDays = Math.max(1, (lastDate - firstDate) / (1000 * 60 * 60 * 24));
        const avgDaysPerRelease = (spanDays / (totalVersions - 1)).toFixed(1);
        lines.push("");
        lines.push(`### Publish Frequency`);
        lines.push(`- Active period: ${Math.round(spanDays)} days`);
        lines.push(`- Average: one release every ${avgDaysPerRelease} days`);
      }

      const text = lines.join("\n");

      return {
        content: [{ type: "text", text }],
        details: {
          package: name,
          totalVersions,
          isNewPackage: !!isNewPackage,
          hasLifecycleScripts,
        },
      };
    },
  };
}

export function makePypiPackageAnalysisTool() {
  return {
    name: "pypi_package_analysis",
    label: "PyPI Package Analysis",
    description:
      "Fetch and summarize metadata for a Python package from PyPI. " +
      "Returns key info: version count, publish dates, maintainers, repository, dependencies, vulnerabilities, etc. " +
      "Use this to investigate Python/PyPI dependencies for supply-chain risk assessment.",
    parameters: Type.Object({
      package_name: Type.String({ description: "The PyPI package name, e.g. 'requests' or 'httpx'" }),
    }),
    execute: async (_toolCallId, params) => {
      const pkg = params.package_name;
      const pypiBase = getConfig().pypiIndexUrl.replace(/\/+$/, "");
      const url = `${pypiBase}/pypi/${encodeURIComponent(pkg)}/json`;

      let data;
      try {
        data = await fetchJson(url);
      } catch (err) {
        if (err.message.includes("404")) {
          return {
            content: [{ type: "text", text: `## PyPI Package Analysis: ${pkg}\n\n**Package does not exist on PyPI.** This is a strong supply-chain risk indicator — the dependency may be typosquatted, removed, or never published.` }],
            details: { package: pkg, exists: false },
          };
        }
        throw new Error(`Failed to fetch PyPI registry for "${pkg}": ${err.message}`);
      }

      const info = data.info || {};
      const releases = data.releases || {};
      const ownership = data.ownership || {};
      const vulnerabilities = data.vulnerabilities || [];

      // --- Basic info ---
      const name = info.name || pkg;
      const summary = info.summary || "(no summary)";
      const license = info.license || "unknown";
      const requiresPython = info.requires_python || "not specified";
      const authorEmail = info.author_email || info.author || "unknown";
      const projectUrls = info.project_urls || {};
      const repoUrl = projectUrls.Source || projectUrls.Homepage || projectUrls.Repository || null;
      const homepage = projectUrls.Homepage || projectUrls.Documentation || info.home_page || null;
      const classifiers = info.classifiers || [];

      // --- Maintainers from ownership ---
      const maintainers = (ownership.roles || []).map(
        (r) => `${r.user} (${r.role})`
      );

      // --- Version / release analysis ---
      const releaseKeys = Object.keys(releases);
      const totalVersions = releaseKeys.length;

      // Extract upload times from release files
      const versionDates = [];
      for (const [ver, files] of Object.entries(releases)) {
        if (files.length > 0) {
          const earliest = files.reduce((min, f) => {
            const t = f.upload_time_iso_8601 || f.upload_time;
            return t && t < min ? t : min;
          }, files[0].upload_time_iso_8601 || files[0].upload_time);
          if (earliest) versionDates.push([ver, earliest]);
        }
      }
      versionDates.sort((a, b) => new Date(a[1]) - new Date(b[1]));

      const firstVersion = versionDates[0] || null;
      const latestVersionStr = info.version || null;
      const latestTime = latestVersionStr && releases[latestVersionStr]?.length
        ? (releases[latestVersionStr][0].upload_time_iso_8601 || releases[latestVersionStr][0].upload_time)
        : versionDates[versionDates.length - 1]?.[1] || null;

      const firstPublishDate = firstVersion ? new Date(firstVersion[1]) : null;
      const now = new Date();
      const threeMonthsAgo = new Date(now);
      threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
      const isNewPackage = firstPublishDate && firstPublishDate > threeMonthsAgo;

      // --- Dependencies ---
      const requiresDist = info.requires_dist || [];
      const coreDeps = requiresDist
        .filter((d) => !d.includes("extra =="))
        .map((d) => d.split(";")[0].trim());
      const optionalDeps = requiresDist
        .filter((d) => d.includes("extra =="));

      // --- Yanked versions ---
      const yankedVersions = [];
      for (const [ver, files] of Object.entries(releases)) {
        if (files.some((f) => f.yanked)) {
          const reason = files.find((f) => f.yanked_reason)?.yanked_reason || "";
          yankedVersions.push(reason ? `${ver} (${reason})` : ver);
        }
      }

      // --- Build text summary ---
      const lines = [];
      lines.push(`## PyPI Package Analysis: ${name}`);
      lines.push("");

      if (isNewPackage) {
        lines.push(`⚠️  **WARNING: This package was first published less than 3 months ago (${firstVersion[1]}). This is a supply-chain risk indicator.**`);
        lines.push("");
      }

      if (vulnerabilities.length > 0) {
        lines.push(`⚠️  **WARNING: ${vulnerabilities.length} known vulnerabilities reported by PyPI.**`);
        for (const v of vulnerabilities) {
          const id = v.id || v.aliases?.[0] || "unknown";
          const detail = v.summary || v.details || "";
          lines.push(`  - ${id}: ${detail.substring(0, 200)}`);
        }
        lines.push("");
      }

      lines.push(`- **Summary**: ${summary}`);
      lines.push(`- **License**: ${license}`);
      lines.push(`- **Requires Python**: ${requiresPython}`);
      lines.push(`- **Total releases**: ${totalVersions}`);
      lines.push(`- **First version**: ${firstVersion ? `${firstVersion[0]} (${firstVersion[1]})` : "unknown"}`);
      lines.push(`- **Latest version**: ${latestVersionStr || "unknown"} (${latestTime || "unknown"})`);
      lines.push(`- **Repository**: ${repoUrl || "not specified"}`);
      if (homepage && homepage !== repoUrl) lines.push(`- **Homepage**: ${homepage}`);
      lines.push(`- **Author**: ${authorEmail}`);
      lines.push(`- **Maintainers**: ${maintainers.length ? maintainers.join(", ") : "none listed"}`);

      // Classifiers - extract dev status
      const devStatus = classifiers.find((c) => c.startsWith("Development Status"));
      if (devStatus) lines.push(`- **Development Status**: ${devStatus.split("::").pop().trim()}`);

      lines.push("");
      lines.push(`### Dependencies`);
      lines.push(`- **Core dependencies** (${coreDeps.length}): ${coreDeps.length ? coreDeps.join(", ") : "none"}`);
      if (optionalDeps.length) {
        lines.push(`- **Optional/extra dependencies** (${optionalDeps.length}): ${optionalDeps.map((d) => d.split(";")[0].trim()).join(", ")}`);
      }
      if (info.provides_extra?.length) {
        lines.push(`- **Extras**: ${info.provides_extra.join(", ")}`);
      }

      if (yankedVersions.length) {
        lines.push("");
        lines.push(`### ⚠️  Yanked Versions (${yankedVersions.length})`);
        lines.push(yankedVersions.join(", "));
      }

      // --- Publish frequency ---
      if (versionDates.length >= 2) {
        const firstDate = new Date(versionDates[0][1]);
        const lastDate = new Date(versionDates[versionDates.length - 1][1]);
        const spanDays = Math.max(1, (lastDate - firstDate) / (1000 * 60 * 60 * 24));
        const avgDaysPerRelease = (spanDays / (versionDates.length - 1)).toFixed(1);
        lines.push("");
        lines.push(`### Publish Frequency`);
        lines.push(`- Active period: ${Math.round(spanDays)} days`);
        lines.push(`- Average: one release every ${avgDaysPerRelease} days`);
      }

      const text = lines.join("\n");

      return {
        content: [{ type: "text", text }],
        details: {
          package: name,
          totalVersions,
          isNewPackage: !!isNewPackage,
          hasVulnerabilities: vulnerabilities.length > 0,
          yankedCount: yankedVersions.length,
        },
      };
    },
  };
}

export function makeUrlAnalysisTool() {
  return {
    name: "url_analysis",
    label: "URL Analysis",
    description:
      "Fetch a URL and return preliminary analysis: HTTP status, content-type, size, redirects, etc.",
    parameters: Type.Object({
      url: Type.String({ description: "The URL to analyze" }),
    }),
    execute: async (_toolCallId, params) => {
      const targetUrl = params.url;
      try {
        const res = await fetch(targetUrl, {
          redirect: "follow",
          signal: AbortSignal.timeout(10_000),
        });
        const body = Buffer.from(await res.arrayBuffer());
        const redirected = res.redirected;
        const finalUrl = res.url;

        const lines = [];
        lines.push(`## URL Analysis: ${targetUrl}`);
        lines.push("");
        if (redirected) {
          lines.push(`- **Redirected**: yes`);
          lines.push(`- **Final URL**: ${finalUrl}`);
        }
        lines.push(`- **Status**: ${res.status} ${res.statusText}`);
        lines.push(`- **Content-Type**: ${res.headers.get("content-type") || "unknown"}`);
        lines.push(`- **Content-Length**: ${res.headers.get("content-length") || "not specified"}`);
        lines.push(`- **Actual Size**: ${body.length} bytes`);
        lines.push(`- **Server**: ${res.headers.get("server") || "unknown"}`);

        const ct = res.headers.get("content-type") || "";
        if (ct.includes("text") || ct.includes("json") || ct.includes("javascript")) {
          const preview = body.toString("utf-8").substring(0, 500);
          lines.push("");
          lines.push(`### Content Preview`);
          lines.push("```");
          lines.push(preview);
          lines.push("```");
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
          details: {
            url: targetUrl,
            finalUrl: redirected ? finalUrl : undefined,
            redirected,
            status: res.status,
            contentType: res.headers.get("content-type") || null,
            size: body.length,
          },
        };
      } catch (err) {
        const isTimeout = err.name === "TimeoutError" || err.code === "ABORT_ERR";
        const statusText = isTimeout ? "timeout (10s)" : "unreachable";
        return {
          content: [{ type: "text", text: `## URL Analysis: ${targetUrl}\n\n- **Status**: ${statusText}\n- **Error**: ${err.message}` }],
          details: { url: targetUrl, status: isTimeout ? "timeout" : "unreachable", error: err.message },
        };
      }
    },
  };
}

export function makeBinaryAnalysisTool(cwd) {
  return {
    name: "binary_analysis",
    label: "Binary Analysis",
    description:
      "Analyze a binary file by running `file` and `strings` on it. Returns file type and notable strings.",
    parameters: Type.Object({
      file_path: Type.String({ description: "Path to the binary file (relative to skill directory)" }),
    }),
    execute: async (_toolCallId, params) => {
      const filePath = params.file_path;
      const absPath = path.resolve(cwd, filePath);
      const lines = [];
      lines.push(`## Binary Analysis: ${filePath}`);
      lines.push("");

      try {
        const stat = fs.statSync(absPath);
        lines.push(`- **Size**: ${stat.size} bytes`);

        try {
          const fileType = execFileSync("file", ["-b", absPath], { encoding: "utf-8", timeout: 5_000 }).trim();
          lines.push(`- **Type**: ${fileType}`);
        } catch { lines.push(`- **Type**: unknown`); }

        // hexdump of first 0x100 bytes
        const fd = fs.openSync(absPath, "r");
        const buf = Buffer.alloc(Math.min(0x100, stat.size));
        fs.readSync(fd, buf, 0, buf.length, 0);
        fs.closeSync(fd);

        lines.push("");
        lines.push(`### Hexdump (first ${buf.length} bytes)`);
        lines.push("```");
        lines.push(...hexdump(buf));
        lines.push("```");

        // extract printable strings (>= 6 chars) from full file
        const found = extractStrings(fs.readFileSync(absPath));
        if (found.length > 0) {
          lines.push("");
          lines.push(`### Notable Strings (first ${found.length})`);
          lines.push("```");
          lines.push(found.join("\n"));
          lines.push("```");
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
          details: { file: filePath, size: stat.size },
        };
      } catch (err) {
        lines.push(`- **Error**: ${err.message}`);
        return {
          content: [{ type: "text", text: lines.join("\n") }],
          details: { file: filePath, status: "error", error: err.message },
        };
      }
    },
  };
}

export function makeBashTool(cwd) {
  return {
    name: "bash",
    label: "Bash",
    description:
      "Execute a shell command and return stdout/stderr. " +
      "Use this to explore the filesystem, read files, etc. " +
      "IMPORTANT: All commands run inside the skill directory. " +
      "Do NOT run commands that modify files or install anything. " +
      "NEVER execute, run, or invoke any target files — no python/node/bash scripts, " +
      "no binary execution, no deserialization (pickle.load, yaml.load, eval, etc.). " +
      "Only use safe read-only commands: cat, head, tail, hexdump, xxd, file, strings, grep, find, ls, wc.",
    parameters: Type.Object({
      command: Type.String({ description: "The shell command to execute" }),
    }),
    execute: async (_toolCallId, params) => {
      try {
        const stdout = execSync(params.command, {
          encoding: "utf-8",
          timeout: 30_000,
          maxBuffer: 1024 * 1024,
          cwd,
        });
        return {
          content: [{ type: "text", text: stdout || "(no output)" }],
          details: { command: params.command },
        };
      } catch (err) {
        const msg = err.stderr || err.stdout || err.message;
        throw new Error(`Command failed: ${msg}`);
      }
    },
  };
}

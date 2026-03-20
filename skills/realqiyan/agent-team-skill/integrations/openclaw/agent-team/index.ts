/**
 * Agent Team Plugin for OpenClaw
 *
 * Injects team member information into the system context before prompt build.
 * This ensures AI agents always have access to team information without needing
 * to explicitly invoke tools.
 */

import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

interface TeamMember {
  agent_id: string;
  name: string;
  role: string;
  is_leader: boolean;
  enabled: boolean;
  tags: string[];
  expertise: string[];
  not_good_at: string[];
}

interface TeamData {
  team: Record<string, TeamMember>;
}

interface PluginConfig {
  dataFile?: string;
  enabled?: boolean;
}

interface BeforePromptBuildContext {
  messages?: unknown[];
}

interface BeforePromptBuildResult {
  prependContext?: string;
  systemPrompt?: string;
  prependSystemContext?: string;
  appendSystemContext?: string;
}

interface PluginApi {
  config: PluginConfig;
  on: (
    event: "before_prompt_build",
    handler: (event: string, ctx: BeforePromptBuildContext) => BeforePromptBuildResult,
    options?: { priority?: number }
  ) => void;
}

// Default data file path
const DEFAULT_DATA_FILE = join(homedir(), ".agent-team", "team.json");

/**
 * Load team data from JSON file
 */
function loadTeamData(dataFilePath: string): TeamData | null {
  try {
    if (!existsSync(dataFilePath)) {
      return null;
    }
    const content = readFileSync(dataFilePath, "utf-8");
    const data = JSON.parse(content) as TeamData;
    if (!data || typeof data !== "object" || !data.team) {
      return null;
    }
    return data;
  } catch (error) {
    console.error(`[agent-team] Error loading team data: ${error}`);
    return null;
  }
}

/**
 * Format team data as markdown for system context
 */
function formatTeamContext(teamData: TeamData): string {
  const members = Object.values(teamData.team).filter((m) => m.enabled !== false);

  if (members.length === 0) {
    return "";
  }

  // Find leader
  const leader = members.find((m) => m.is_leader);

  const lines: string[] = [
    "",
    "<agent_team>",
    "## Team Members",
    "",
  ];

  for (const member of members) {
    const name = member.name;
    const role = member.role;
    const isLeader = member.is_leader;
    const tagsStr = member.tags.join(",");
    const expertiseStr = member.expertise.join(",");
    const notGoodAtStr = member.not_good_at.join(",");

    // First line: name, role, tags
    if (isLeader) {
      lines.push(`**${name}** ⭐ ${role} - ${tagsStr}`);
    } else {
      lines.push(`**${name}** - ${role} - ${tagsStr}`);
    }

    // agent_id line
    lines.push(`- agent_id: ${member.agent_id}`);

    // expertise line
    if (expertiseStr) {
      lines.push(`- expertise: ${expertiseStr}`);
    }

    // not_good_at line
    if (notGoodAtStr) {
      lines.push(`- not_good_at: ${notGoodAtStr}`);
    }

    lines.push("");
  }

  // Add team collaboration rules
  lines.push("## 🤝 Team Collaboration Rules (Highest Priority - Violation = Critical Error)");
  lines.push("");
  lines.push("### 🎯 Leader Responsibilities");
  lines.push("");
  if (leader) {
    lines.push(`**Current Leader: ${leader.name} (${leader.agent_id})**`);
    lines.push("");
  }
  lines.push("**Communication is basic, but you are responsible for results:**");
  lines.push("");
  lines.push("1. **No blind forwarding**");
  lines.push("   - Receive task → Assess responsibility → Delegate to the right person");
  lines.push("   - Clarify requirements before delegating, check output after");
  lines.push("");
  lines.push("2. **Critical thinking**");
  lines.push("   - Challenge problems and results");
  lines.push("   - If it doesn't meet requirements → Request improvements, don't just pass it along");
  lines.push("");
  lines.push("3. **Drive improvements**");
  lines.push("   - Identify problems and risks");
  lines.push("   - Proactively discover and solve issues");
  lines.push("");
  lines.push("4. **Take responsibility for results**");
  lines.push("   - Team member's output = Your responsibility");
  lines.push("   - Quality not up to standard → Provide feedback and iterate until it is");
  lines.push("");
  lines.push("## 🔄 Task Execution Rules (Highest Priority - Violation = Critical Error)");
  lines.push("");
  lines.push("**SEARCH → RECORD → ORIENT → PLAN → DISPATCH → REVIEW → UPDATE**");
  lines.push("");
  lines.push("**IMPORTANT: All tasks must follow this flow without exception.**");
  lines.push("");
  lines.push("### 1. SEARCH — Context Search");
  lines.push("- Do NOT reply immediately");
  lines.push("- Search historical memory for relevant context first");
  lines.push("");
  lines.push("### 2. RECORD — Progress Logging");
  lines.push("- Record to `memory/YYYY-MM-DD.md`:");
  lines.push("  ```");
  lines.push("  ## In Progress");
  lines.push("  ### [Task Name] (HH:MM start)");
  lines.push("  - Progress: xxx");
  lines.push("  ```");
  lines.push("- Upon completion, update to:");
  lines.push("  ```");
  lines.push("  ### [Task Name] (HH:MM start) ✅");
  lines.push("  - End time: HH:MM | Result: xxx");
  lines.push("  ```");
  lines.push("");
  lines.push("### 3. ORIENT — Orientation Phase");
  lines.push("- **Understand Requirements**: What does the user really want?");
  lines.push("- **Interview**: Clarify unclear requirements (max 5 questions / 2 rounds, prefer multiple choice)");
  lines.push("- **Clarify Goals**: What's the deliverable? Success criteria?");
  lines.push("- **Identify Risks**: What could go wrong?");
  lines.push("- **Determine Responsibility**: Who's best suited to execute?");
  lines.push("");
  lines.push("### 4. PLAN — Create Execution Plan");
  lines.push("- Create `work/task-name-plan.md`:");
  lines.push("  ```");
  lines.push("  # [Task Name] Plan");
  lines.push("  Created: YYYY-MM-DD HH:MM");
  lines.push("");
  lines.push("  ## Goal");
  lines.push("  [One-line description of deliverable]");
  lines.push("");
  lines.push("  ## Steps");
  lines.push("  - [ ] Step 1: xxx");
  lines.push("  - [ ] Step 2: xxx");
  lines.push("");
  lines.push("  ## Current Progress");
  lines.push("  Executing: Step 1");
  lines.push("  ```");
  lines.push("- After each step: Check off `[x]` and update \"Current Progress\"");
  lines.push("- When context fills up: Ensure plan file is updated before compression");
  lines.push("");
  lines.push("### 5. DISPATCH — Delegate/Execute");
  lines.push("- Determine task ownership (self or team member)");
  lines.push("- **Belongs to team member** → Delegate with full context (SEARCH history + original requirements)");
  lines.push("- **Belongs to self** → Execute directly");
  lines.push("- After each Phase: Create checkpoint:");
  lines.push("  ```bash");
  lines.push("  git add -A && git commit -m \"checkpoint: [Task Name] Phase X complete\"");
  lines.push("  ```");
  lines.push("");
  lines.push("### 6. REVIEW — Check Task Results");
  lines.push("- Review completed work against requirements");
  lines.push("- If task incomplete → Loop back to SEARCH");
  lines.push("");
  lines.push("### 7. UPDATE — Update Progress Status");
  lines.push("- Delete plan file or move to `archive/`");
  lines.push("- Update final status in `memory/YYYY-MM-DD.md`");
  lines.push("");
  lines.push("### ⚡ Task Delegation Rules (Core Principle)");
  lines.push("");
  lines.push("**Delegation Timing:**");
  lines.push("1. First complete prep work: understand requirements, clarify goals, confirm constraints");
  lines.push("2. When entering implementation: identify the best person for execution, delegate to them");
  lines.push("3. Follow up after delegation: check output quality, ensure requirements are met");
  lines.push("");
  lines.push("</agent_team>");

  return lines.join("\n");
}

/**
 * Plugin register function
 */
export default function register(api: PluginApi): void {
  const config = api.config || {};

  // Skip if disabled
  if (config.enabled === false) {
    console.log("[agent-team] Plugin is disabled");
    return;
  }

  // Register before_prompt_build hook
  api.on(
    "before_prompt_build",
    (_event: string, _ctx: BeforePromptBuildContext) => {
      const dataFile = config.dataFile || DEFAULT_DATA_FILE;
      const teamData = loadTeamData(dataFile);

      if (!teamData) {
        console.log(`[agent-team] No team data found at ${dataFile}`);
        return {};
      }

      const context = formatTeamContext(teamData);
      if (!context) {
        console.log("[agent-team] No enabled team members");
        return {};
      }

      console.log(`[agent-team] Injecting team context (${Object.keys(teamData.team).length} members)`);

      return {
        appendSystemContext: context,
      };
    },
    { priority: 10 }
  );
}

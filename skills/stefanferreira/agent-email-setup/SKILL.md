---
name: agent-email-setup
description: Set up dedicated email accounts for AI agents with proper workflows. Use when agents need external communications (Lourens for sysadmin, Ace for competitions). Always test in sandbox first, document configuration, then deploy to production.
---

# Agent Email Setup

## Purpose

Provide dedicated email accounts for AI agents with clear role separation and approval workflows. Prevents mixing of responsibilities (e.g., Ace shouldn't handle Contabo support tickets).

## When to Use

**Set up email for agent when:**
- Agent needs external communications (Lourens, Ace)
- Role separation is important
- Audit trail needed for communications
- Professional identity required

**Do NOT set up email for:**
- Internal-only agents (Bob, Scout)
- Agents without external communication needs
- Temporary/task-specific agents

## Architecture

### Email Address Strategy
```
@supplystoreafrica.com domain:
- lourens@      → SysAdmin (infrastructure, support tickets)
- ace@          → Competitions (entries, prize notifications)
- facet@        → CAD (manufacturer communications) - if needed
```

### Forwarding Rules
- All agent emails forward to: `stef.personal@gmail.com`
- CC on all sent emails: `stef.personal@gmail.com`
- Maintain separate sent folders per agent

### Role Separation
| Agent | Email | Purpose | External Comms |
|-------|-------|---------|----------------|
| Lourens | lourens@ | Infrastructure, support tickets, system issues | ✅ Required |
| Ace | ace@ | Competition entries, prize notifications | ✅ Required |
| Facet | facet@ | Manufacturer inquiries, technical specs | ⚠️ Optional |
| Bob | - | Internal coordination only | ❌ Not needed |
| Scout | - | Research, no external comms | ❌ Not needed |

## Workflow

### 1. Sandbox Testing (ALWAYS FIRST)
```bash
# Create sandbox environment
python3 /root/.openclaw/workspace/sandbox_lourens_email.py

# Test configuration
cd /tmp/lourens_email_sandbox_*/ && python3 test_email_workflow.py
```

### 2. Production Setup

#### Step 1: Create Email Account
1. Log into hosting control panel
2. Create email account: `agentname@supplystoreafrica.com`
3. Set strong password (store in Bitwarden)
4. Configure forwarding to `stef.personal@gmail.com`

#### Step 2: Configure IMAP/SMTP
```json
{
  "imap_server": "mail.supplystoreafrica.com",
  "imap_port": 993,
  "smtp_server": "mail.supplystoreafrica.com", 
  "smtp_port": 587,
  "username": "agentname@supplystoreafrica.com",
  "password": "{{BITWARDEN_PASSWORD}}"
}
```

#### Step 3: Agent Configuration
Add to agent's workspace:
```bash
# Create email config
mkdir -p /root/.openclaw/agents/{agent}/workspace/email/
cat > /root/.openclaw/agents/{agent}/workspace/email/config.json << 'EOF'
{{
  "email": "{agent}@supplystoreafrica.com",
  "display_name": "{Agent Name} {Role}",
  "signature": "Best regards,\\n\\n{Agent Name}\\n{Role} Agent\\nSupply Store Africa\\n{agent}@supplystoreafrica.com",
  "forward_to": ["stef.personal@gmail.com"],
  "auto_cc": ["stef.personal@gmail.com"]
}}
EOF
```

#### Step 4: Update OpenClaw Configuration
```bash
# Add email tools to agent
openclaw config set agents.list[{index}].tools.allow+=email_send
openclaw config set agents.list[{index}].tools.allow+=email_check
```

### 3. Email Templates

#### Generic Template
```markdown
TO: {recipient}
FROM: {Agent Name} {Role} <{agent}@supplystoreafrica.com>
CC: Stef Ferreira <stef.personal@gmail.com>
SUBJECT: {subject}
DATE: {date}

{greeting},

{body}

{signature}
```

#### Contabo Support Template (Lourens)
```markdown
TO: support@contabo.com
FROM: Lourens SysAdmin <lourens@supplystoreafrica.com>
CC: Stef Ferreira <stef.personal@gmail.com>
SUBJECT: {ticket_subject}
DATE: {date}

Dear {support_agent},

{content}

Current system status:
- VPS: 161.97.110.234
- Ticket: {ticket_number}
- Issue: {issue_description}

We appreciate your assistance.

Best regards,

Lourens
SysAdmin Agent
Supply Store Africa
lourens@supplystoreafrica.com
```

#### Competition Entry Template (Ace)
```markdown
TO: competitions@company.com
FROM: Ace Competitions <ace@supplystoreafrica.com>
CC: Stef Ferreira <stef.personal@gmail.com>
SUBJECT: Entry: {competition_name}
DATE: {date}

Dear Competition Team,

Please accept my entry for {competition_name}.

{entry_details}

Thank you for this opportunity.

Best regards,

Ace
Competitions Agent
Supply Store Africa
ace@supplystoreafrica.com
```

### 4. Approval Workflow

**ALL external emails require approval:**
1. Draft created in `/root/.openclaw/workspace/drafts/`
2. Presented to Stef in chat interface
3. Wait for explicit "approved" or "send it"
4. Send only after approval
5. Log sent email

**Approval triggers:**
- "Approved"
- "Send it" 
- "Go ahead"
- "Yes, send that"

**NOT approved by:**
- "Looks good" (ambiguous)
- "OK" (ambiguous)
- Silence (never assume)

### 5. Migration Process

**When moving communications between agents:**
1. Set up new agent email
2. Forward thread to new agent email
3. Send notification: "Future communications: newagent@supplystoreafrica.com"
4. Update contact information with external party
5. Archive old agent's involvement

**Example: Contabo migration from Ace to Lourens**
1. Create `lourens@supplystoreafrica.com`
2. Forward Contabo thread to Lourens
3. Email Contabo: "Future updates: lourens@supplystoreafrica.com"
4. Ace focuses only on competitions

## Testing Checklist

### Sandbox Test
- [ ] Configuration files created
- [ ] Templates work correctly
- [ ] Draft generation tested
- [ ] Approval workflow simulated
- [ ] No syntax errors

### Production Test
- [ ] Email account created
- [ ] IMAP/SMTP connectivity
- [ ] Send test email (to self)
- [ ] Receive test email
- [ ] Forwarding to stef.personal@gmail.com works
- [ ] CC on sent emails works

### Integration Test
- [ ] Agent can access email
- [ ] Draft creation works
- [ ] Approval workflow functional
- [ ] Sent emails logged
- [ ] Error handling works

## Error Handling

### Common Issues
1. **IMAP connection failed**: Check credentials, firewall, port
2. **SMTP rejected**: Check authentication, port 587 vs 465
3. **Email not forwarding**: Check hosting panel settings
4. **CC not working**: Check email client configuration

### Recovery Procedures
```bash
# Test IMAP
openssl s_client -connect mail.supplystoreafrica.com:993 -crlf

# Test SMTP
openssl s_client -connect mail.supplystoreafrica.com:587 -starttls smtp

# Check logs
tail -f /var/log/mail.log
```

## Security

### Credential Management
- Store passwords in Bitwarden
- Never hardcode in scripts
- Use environment variables
- Rotate passwords periodically

### Access Control
- Agents only access their own email
- No cross-agent email access
- All emails CC'd to human oversight
- Sent items archived for audit

### Monitoring
- Failed login attempts logged
- Unusual sending patterns flagged
- Regular access review
- Password rotation schedule

## Maintenance

### Daily
- Check sent items logged
- Verify forwarding working
- Monitor for failed sends

### Weekly
- Review email logs
- Check storage quotas
- Update templates if needed

### Monthly
- Password rotation
- Audit access logs
- Review security settings

## Related Skills
- `email-approval-workflow` - Draft and approval process
- `gmail-gog-setup` - Alternative email configuration
- `secure-secret-sharing` - For credential sharing if needed
- `agent-lourens` - Lourens-specific configuration
- `ace-competitions` - Ace-specific configuration

## Critical: Agent Knowledge Transfer Protocol

**Issue Discovered (March 31, 2026):** Facet reported "I have no skills, haven't learned anything yet"  
**Root Cause:** Agents configured but had empty workspaces - no knowledge transfer

### What MUST Be Transferred When Creating Agents
1. **Identity** - Who they are (IDENTITY.md, SOUL.md)
2. **User Context** - Who Stef is (USER.md)  
3. **System Knowledge** - What we've built (MEMORY.md, AGENTS.md)
4. **Skills & Learning** - What they can do (skill-specific docs)
5. **Memory & History** - What we've learned (memory/ files)
6. **Tool Access** - read tool required to access workspace

### Knowledge Transfer Procedure
```bash
# Run knowledge transfer script
python3 /root/.openclaw/workspace/setup_agent_knowledge.py --agent {agent_name}

# Verify transfer
ls -la /root/.openclaw/agents/{agent}/workspace/
cat /root/.openclaw/agents/{agent}/workspace/IDENTITY.md
```

### Protocol Document
- `AGENT_TRANSFORMATION_PROTOCOL.md` - Complete transfer procedure
- `setup_agent_knowledge.py` - Automation script

**Result:** All agents (Lourens, Ace, Scout, Facet) now have complete knowledge and are proper assistants.

## Lessons Learned

### From Contabo Experience:
1. **Role confusion**: Ace shouldn't handle infrastructure emails
2. **Email identity**: Professional email addresses matter
3. **Approval workflow**: Essential for external communications
4. **Migration planning**: Need clear handover process

### From Knowledge Transfer Issue:
1. **Empty workspaces**: Agents need complete knowledge transfer
2. **Identity files**: Must include IDENTITY.md, SOUL.md, USER.md
3. **System context**: MEMORY.md and AGENTS.md essential
4. **Tool access**: read tool required to access workspace files

### Best Practices:
1. Always sandbox test first
2. Document configuration thoroughly
3. Maintain role separation
4. Human oversight on all external comms
5. Regular security reviews
6. Complete knowledge transfer for new agents
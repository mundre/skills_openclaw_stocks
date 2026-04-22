---
name: skylv-api-status-checker
slug: skylv-api-status-checker
version: 1.0.0
description: "Checks API health and uptime. Monitors endpoints and validates responses. Triggers: check api status, api health, monitor uptime."
author: SKY-lv
license: MIT
tags: [automation, tools]
keywords: [automation, tools]
triggers: api-status-checker
---

# API Status Checker

## Overview
Monitors API endpoints for health and uptime.

## When to Use
- User asks to "check if API is up"
- Debugging API failures

## Status Evaluation
200 in <500ms = HEALTHY
200 in 500ms-2s = DEGRADED
200 in >2s = SLOW
4xx = CLIENT_ERROR
5xx = SERVER_ERROR
Timeout = DOWN

## Check Command
$result = Invoke-WebRequest -Uri "https://api.example.com/health" -Method GET -TimeoutSec 10
if ($result.StatusCode -eq 200) { "OK" } else { "FAIL: " + $result.StatusCode }

## Alert Thresholds
- Response time > 2s = WARNING
- 5xx response = CRITICAL
- Timeout = CRITICAL

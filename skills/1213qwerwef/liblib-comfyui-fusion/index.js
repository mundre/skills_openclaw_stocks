#!/usr/bin/env node

const { spawn } = require("child_process");

const args = process.argv.slice(2);

// 默认调用你的 python 脚本
const py = spawn("python3", ["client.py", ...args], {
  stdio: "inherit"
});

py.on("close", (code) => {
  process.exit(code);
});
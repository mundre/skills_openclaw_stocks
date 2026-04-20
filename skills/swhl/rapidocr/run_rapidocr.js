const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const https = require('https');

function commandExists(cmd) {
  const checker = process.platform === 'win32' ? 'where' : 'which';
  const result = spawnSync(checker, [cmd], { encoding: 'utf8', shell: false });
  return result.status === 0 && result.stdout && result.stdout.trim();
}

function buildRapidOcrCandidatePaths() {
  const candidates = [];
  const home = os.homedir();
  if (process.platform === 'win32') {
    const localAppData = process.env.LOCALAPPDATA || path.join(home, 'AppData', 'Local');
    const appData = process.env.APPDATA || path.join(home, 'AppData', 'Roaming');
    const pyLauncher = spawnSync('py', ['-0p'], { encoding: 'utf8', shell: false });
    if (pyLauncher.status === 0 && pyLauncher.stdout) {
      const lines = pyLauncher.stdout.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
      for (const line of lines) {
        const m = line.match(/^(?:-[0-9.]+-64\s+)?(.+?python(?:w)?\.exe)$/i);
        const exe = m ? m[1] : line;
        if (exe.toLowerCase().endsWith('.exe')) {
          candidates.push(path.join(path.dirname(exe), 'Scripts', 'rapidocr.exe'));
          candidates.push(path.join(path.dirname(exe), 'Scripts', 'rapidocr_onnxruntime.exe'));
        }
      }
    }
    const versions = ['313', '312', '311', '310', '39', '38', '37'];
    for (const v of versions) {
      candidates.push(path.join(localAppData, 'Programs', 'Python', `Python${v}`, 'Scripts', 'rapidocr.exe'));
      candidates.push(path.join(localAppData, 'Programs', 'Python', `Python${v}`, 'Scripts', 'rapidocr_onnxruntime.exe'));
      candidates.push(path.join(appData, 'Python', `Python${v}`, 'Scripts', 'rapidocr.exe'));
      candidates.push(path.join(appData, 'Python', `Python${v}`, 'Scripts', 'rapidocr_onnxruntime.exe'));
    }
  }
  return [...new Set(candidates)];
}

function resolveRapidOCR() {
  const names = process.platform === 'win32'
    ? ['rapidocr.exe', 'rapidocr_onnxruntime.exe', 'rapidocr']
    : ['rapidocr', 'rapidocr_onnxruntime'];
  for (const name of names) {
    const found = commandExists(name);
    if (found) return found.split(/\r?\n/)[0].trim();
  }
  for (const candidate of buildRapidOcrCandidatePaths()) {
    if (candidate && fs.existsSync(candidate)) return candidate;
  }
  return null;
}

function resolvePython() {
  const candidates = process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
  for (const name of candidates) {
    const found = commandExists(name);
    if (found) return found.split(/\r?\n/)[0].trim();
  }
  return null;
}

function cleanToken(s) {
  return String(s || '').trim().replace(/^['"]+|['"]+$/g, '');
}

function isImagePathCandidate(s) {
  const v = cleanToken(s);
  return /\.(png|jpg|jpeg|webp|bmp|tif|tiff)$/i.test(v);
}

function tryExistingPath(s) {
  const v = cleanToken(s);
  if (!v) return null;
  if (isImagePathCandidate(v) && fs.existsSync(v)) return v;
  return null;
}

function extractWindowsPaths(text) {
  const s = String(text || '');
  return s.match(/[A-Za-z]:\\[^\r\n"'<>|?*]+?\.(?:png|jpg|jpeg|webp|bmp|tif|tiff)/gi) || [];
}

function extractPosixPaths(text) {
  const s = String(text || '');
  return s.match(/\/(?:[^\s"'<>|?*]+\/)*[^\s"'<>|?*]+\.(?:png|jpg|jpeg|webp|bmp|tif|tiff)/gi) || [];
}

function extractUrl(text) {
  const s = String(text || '');
  const m = s.match(/https?:\/\/[^\s"'<>]+?\.(?:png|jpg|jpeg|webp|bmp|tif|tiff)(?:\?[^\s"'<>]*)?/i);
  return m ? m[0] : null;
}

function parseOptions(text) {
  const s = String(text || '');
  return {
    json: /(^|\s)--json(\s|$)|\bjson输出\b|\b返回json\b|\bjson格式\b|\b结构化\b/i.test(s),
  };
}

function extractImagePathFromText(text) {
  if (!text) return null;
  if (typeof text !== 'string') {
    try { text = JSON.stringify(text); } catch { text = String(text); }
  }
  try {
    const obj = JSON.parse(text);
    if (obj && typeof obj === 'object') {
      const candidates = [obj.img_path, obj.image_path, obj.path, obj.file, obj.file_path, obj.image];
      for (const c of candidates) {
        const p = tryExistingPath(c);
        if (p) return p;
      }
      for (const c of candidates) {
        if (typeof c === 'string' && /^https?:\/\//i.test(c)) return c;
      }
      if (obj.args && typeof obj.args === 'object') {
        const c2 = [obj.args.img_path, obj.args.image_path, obj.args.path, obj.args.file, obj.args.file_path, obj.args.image];
        for (const c of c2) {
          const p = tryExistingPath(c);
          if (p) return p;
        }
        for (const c of c2) {
          if (typeof c === 'string' && /^https?:\/\//i.test(c)) return c;
        }
      }
    }
  } catch {}

  const explicitPatterns = [
    /img_path\s*[=:]\s*([^\r\n]+)/i,
    /image_path\s*[=:]\s*([^\r\n]+)/i,
    /file_path\s*[=:]\s*([^\r\n]+)/i,
    /图片路径[是为：:]\s*([^\r\n]+)/i,
    /图片链接[是为：:]\s*([^\r\n]+)/i,
    /图片url[是为：:]\s*([^\r\n]+)/i,
  ];
  for (const re of explicitPatterns) {
    const m = text.match(re);
    if (m && m[1]) {
      const segment = cleanToken(m[1]);
      const direct = tryExistingPath(segment);
      if (direct) return direct;
      const url = extractUrl(segment);
      if (url) return url;
      for (const c of [...extractWindowsPaths(segment), ...extractPosixPaths(segment)]) {
        const p = tryExistingPath(c);
        if (p) return p;
      }
    }
  }

  const inlineUrl = extractUrl(text);
  if (inlineUrl) return inlineUrl;
  for (const c of [...extractWindowsPaths(text), ...extractPosixPaths(text)]) {
    const p = tryExistingPath(c);
    if (p) return p;
  }
  const tokens = text.split(/\s+/).map(cleanToken).filter(Boolean);
  for (const token of tokens) {
    const p = tryExistingPath(token);
    if (p) return p;
    if (/^https?:\/\//i.test(token)) return token;
  }
  return null;
}

function resolveInput(argv) {
  const positional = (argv || []).slice(2);
  const rawText = positional.join(' ');
  const envCandidates = [process.env.SKILL_ARGS, process.env.SKILL_INPUT, process.env.SKILL_USER_PROMPT, process.env.INPUT, process.env.USER_PROMPT, process.env.ARGS, process.env.ARGUMENTS, process.env.PROMPT].filter(Boolean);
  let source = null;

  for (const arg of positional) {
    const direct = tryExistingPath(arg);
    if (direct) { source = direct; break; }
  }
  if (!source) {
    for (const arg of positional) {
      if (arg === '<用户原话>' || arg === '{input}' || arg === '{{input}}' || arg === '{user_prompt}' || arg === '{{user_prompt}}') continue;
      const found = extractImagePathFromText(arg);
      if (found) { source = found; break; }
    }
  }
  if (!source) {
    for (const text of envCandidates) {
      const found = extractImagePathFromText(text);
      if (found) { source = found; break; }
    }
  }
  return { source, options: parseOptions(rawText || envCandidates.join(' ')), rawText, envText: envCandidates.join(' ') };
}

function inferExtFromUrl(url) {
  const m = String(url).match(/\.(png|jpg|jpeg|webp|bmp|tif|tiff)(?:\?|#|$)/i);
  return m ? m[1].toLowerCase() : 'png';
}

function downloadToTemp(url) {
  return new Promise((resolve, reject) => {
    const client = /^https:/i.test(url) ? https : http;
    const ext = inferExtFromUrl(url);
    const dir = path.join(os.tmpdir(), 'rapidocr-inputs');
    fs.mkdirSync(dir, { recursive: true });
    const filePath = path.join(dir, `rapidocr_${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`);
    const file = fs.createWriteStream(filePath);
    const req = client.get(url, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        file.close();
        fs.unlink(filePath, () => {});
        return resolve(downloadToTemp(res.headers.location));
      }
      if (res.statusCode !== 200) {
        file.close();
        fs.unlink(filePath, () => {});
        return reject(new Error(`Download failed: HTTP ${res.statusCode}`));
      }
      res.pipe(file);
      file.on('finish', () => file.close(() => resolve(filePath)));
    });
    req.on('error', (err) => {
      file.close();
      fs.unlink(filePath, () => {});
      reject(err);
    });
  });
}

function normalizeCliOutput(stdout, localPath, jsonMode) {
  const text = String(stdout || '').trim();
  let lines = [];
  let scores = [];
  if (/txts=\(/.test(text)) {
    const m = text.match(/txts=\((.*?)\),\s*scores=/s);
    if (m && m[1]) {
      lines = m[1].split(/,\s*/).map(s => s.trim().replace(/^['"]|['"]$/g, '')).filter(Boolean);
    }
    const s = text.match(/scores=\((.*?)\)(?:,|\))/s);
    if (s && s[1]) {
      scores = s[1].split(/,\s*/).map(x => Number(x)).filter(x => !Number.isNaN(x));
    }
  }
  if (!lines.length) {
    lines = text ? text.split(/\r?\n/).map(s => s.trim()).filter(Boolean) : [];
  }
  if (!jsonMode) return lines.join('\n');
  return JSON.stringify({ text: lines.join('\n'), lines, boxes: [], scores, source: localPath });
}

function runRapidOcrCli(imgPath, jsonMode) {
  const cmd = resolveRapidOCR();
  if (!cmd) return { ok: false, code: 127 };
  const result = spawnSync(cmd, ['-img', imgPath], { encoding: 'utf8', shell: false, env: { ...process.env, PYTHONWARNINGS: 'ignore' } });
  const stdout = result.stdout || '';
  const stderr = (result.stderr || '').split(/\r?\n/).filter(line => {
    if (!line) return false;
    if (/RequestsDependencyWarning/i.test(line)) return false;
    return true;
  }).join('\n').trim();
  if ((result.status ?? 1) !== 0) return { ok: false, code: result.status ?? 1, stderr };
  process.stdout.write(normalizeCliOutput(stdout, imgPath, jsonMode) + '\n');
  return { ok: true, code: 0 };
}

function runPythonOCR(imgPath, jsonMode) {
  const python = resolvePython();
  if (!python) return { ok: false, code: 127, stderr: 'Python executable not found.' };
  const script = [
    'import sys, warnings, logging, json',
    'warnings.filterwarnings("ignore")',
    'for name in ["RapidOCR", "rapidocr", "onnxruntime"]:',
    '    logger = logging.getLogger(name)',
    '    logger.handlers.clear()',
    '    logger.propagate = False',
    '    logger.setLevel(logging.CRITICAL)',
    'logging.disable(logging.CRITICAL)',
    'from rapidocr import RapidOCR',
    'img_path = sys.argv[1]',
    'json_mode = sys.argv[2] == "1"',
    'engine = RapidOCR()',
    'result = engine(img_path)',
    'lines = []',
    'boxes = []',
    'scores = []',
    'if result is None:',
    '    print(json.dumps({"text":"","lines":[],"boxes":[],"scores":[],"source":img_path}, ensure_ascii=False) if json_mode else "")',
    '    sys.exit(0)',
    'if hasattr(result, "txts") and result.txts:',
    '    lines = [str(x) for x in result.txts]',
    'if hasattr(result, "scores") and result.scores:',
    '    try: scores = [float(x) for x in result.scores]',
    '    except Exception: scores = [str(x) for x in result.scores]',
    'if hasattr(result, "boxes") and result.boxes is not None:',
    '    try: boxes = result.boxes.tolist()',
    '    except Exception: boxes = []',
    'if (not lines) and isinstance(result, (list, tuple)):',
    '    for item in result:',
    '        if isinstance(item, (list, tuple)) and len(item) >= 2:',
    '            lines.append(str(item[1]))',
    'if json_mode:',
    '    print(json.dumps({"text":"\\n".join(lines),"lines":lines,"boxes":boxes,"scores":scores,"source":img_path}, ensure_ascii=False))',
    'else:',
    '    print("\\n".join(lines))'
  ].join('\n');
  const env = { ...process.env, PYTHONWARNINGS: 'ignore', LOG_LEVEL: 'CRITICAL', RAPIDOCR_LOG_LEVEL: 'CRITICAL' };
  const args = python.toLowerCase().endsWith('py.exe') || path.basename(python).toLowerCase() === 'py'
    ? ['-3', '-c', script, imgPath, jsonMode ? '1' : '0']
    : ['-c', script, imgPath, jsonMode ? '1' : '0'];
  const result = spawnSync(python, args, { encoding: 'utf8', shell: false, env });
  if ((result.status ?? 1) !== 0) {
    const stderr = (result.stderr || '').split(/\r?\n/).filter(line => {
      if (!line) return false;
      if (/RequestsDependencyWarning/i.test(line)) return false;
      if (/warnings\.warn\(/i.test(line)) return false;
      if (/\[INFO\]/i.test(line)) return false;
      if (/Using engine_name/i.test(line)) return false;
      if (/File exists and is valid/i.test(line)) return false;
      if (/main\.py:57/i.test(line)) return false;
      if (/download_file\.py:60/i.test(line)) return false;
      if (/base\.py:22/i.test(line)) return false;
      return true;
    }).join('\n').trim();
    return { ok: false, code: result.status ?? 1, stderr };
  }
  if (result.stdout && result.stdout.trim()) process.stdout.write(result.stdout.trim() + '\n');
  return { ok: true, code: 0 };
}

async function main() {
  const { source, options } = resolveInput(process.argv);
  if (!source) {
    console.error('Missing image path or image URL.');
    process.exit(2);
  }
  let localPath = source;
  if (/^https?:\/\//i.test(source)) localPath = await downloadToTemp(source);
  const cliResult = runRapidOcrCli(localPath, options.json);
  if (cliResult.ok) process.exit(0);
  const pyResult = runPythonOCR(localPath, options.json);
  if (pyResult.ok) process.exit(0);
  console.error(pyResult.stderr || cliResult.stderr || 'RapidOCR execution failed.');
  process.exit(pyResult.code || cliResult.code || 1);
}

main().catch(err => {
  console.error(err && err.message ? err.message : String(err));
  process.exit(1);
});

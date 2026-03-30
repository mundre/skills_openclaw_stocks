#!/usr/bin/env node
/**
 * Bumblebee Lyric Engine 🐝🎵
 * 
 * Fetches synced lyrics from LRCLIB, indexes them by phrase,
 * and lets an AI compose messages from exact lyric lines.
 * 
 * Usage:
 *   node lyric-engine.js index <artist> <track>     — Index a song's lyrics
 *   node lyric-engine.js search <phrase>             — Find lyric lines matching a phrase
 *   node lyric-engine.js compose <message>           — AI-style: find lyrics that say the message
 *   node lyric-engine.js speak <line_id> [line_id..] — Play specific lyric lines on Spotify
 *   node lyric-engine.js catalog                     — Show all indexed songs + lines
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// Configurable paths — override with env vars or defaults to workspace layout
const WORKSPACE = process.env.BUMBLEBEE_WORKSPACE || path.join(__dirname, '..', '..', '..', 'projects');
const SPOTIFY_DIR = process.env.SPOTIFY_DIR || path.join(WORKSPACE, 'spotify');
const TOKENS_FILE = path.join(SPOTIFY_DIR, 'tokens.json');
const ENV_FILE = path.join(SPOTIFY_DIR, '.env');
const INDEX_FILE = process.env.BUMBLEBEE_INDEX || path.join(__dirname, 'lyric-index.json');

// --- LRCLIB API ---

function lrcSearch(artist, track) {
  return new Promise((resolve, reject) => {
    const q = encodeURIComponent(`${track} ${artist}`);
    const options = {
      hostname: 'lrclib.net',
      path: `/api/search?q=${q}`,
      headers: { 'User-Agent': 'Bumblebee/1.0' },
    };
    https.get(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve([]); }
      });
    }).on('error', reject);
  });
}

function parseLRC(syncedLyrics) {
  if (!syncedLyrics) return [];
  const lines = [];
  for (const line of syncedLyrics.split('\n')) {
    const match = line.match(/\[(\d+):(\d+\.\d+)\]\s*(.*)/);
    if (match) {
      const min = parseInt(match[1]);
      const sec = parseFloat(match[2]);
      const ms = Math.round((min * 60 + sec) * 1000);
      const text = match[3].trim();
      if (text) lines.push({ ms, text });
    }
  }
  return lines;
}

// --- Spotify ---

function loadTokens() {
  return JSON.parse(fs.readFileSync(TOKENS_FILE, 'utf8'));
}

function saveTokens(tokens) {
  tokens.obtained_at = new Date().toISOString();
  fs.writeFileSync(TOKENS_FILE, JSON.stringify(tokens, null, 2));
}

function loadEnv() {
  const env = {};
  const lines = fs.readFileSync(ENV_FILE, 'utf8').split('\n');
  for (const line of lines) {
    const [key, ...val] = line.split('=');
    if (key && val.length) env[key.trim()] = val.join('=').trim();
  }
  return env;
}

function spotifyRequest(method, endpoint, body = null) {
  return new Promise((resolve, reject) => {
    const tokens = loadTokens();
    const options = {
      hostname: 'api.spotify.com',
      path: endpoint,
      method,
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      },
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 401) {
          refreshToken().then(() => {
            spotifyRequest(method, endpoint, body).then(resolve).catch(reject);
          }).catch(reject);
          return;
        }
        try { resolve(data ? JSON.parse(data) : { status: res.statusCode }); }
        catch { resolve({ raw: data, status: res.statusCode }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function refreshToken() {
  return new Promise((resolve, reject) => {
    const tokens = loadTokens();
    const env = loadEnv();
    const auth = Buffer.from(`${env.SPOTIFY_CLIENT_ID}:${env.SPOTIFY_CLIENT_SECRET}`).toString('base64');
    const postData = `grant_type=refresh_token&refresh_token=${tokens.refresh_token}`;
    const options = {
      hostname: 'accounts.spotify.com',
      path: '/api/token',
      method: 'POST',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(postData),
      },
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const newTokens = JSON.parse(data);
        if (newTokens.access_token) {
          if (!newTokens.refresh_token) newTokens.refresh_token = tokens.refresh_token;
          newTokens.scope = newTokens.scope || tokens.scope;
          saveTokens(newTokens);
          resolve();
        } else reject(new Error('Token refresh failed'));
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function searchSpotifyTrack(artist, track) {
  const q = encodeURIComponent(`${track} ${artist}`);
  const result = await spotifyRequest('GET', `/v1/search?q=${q}&type=track&limit=1&market=MX`);
  const items = result?.tracks?.items;
  if (items && items.length > 0) {
    return {
      uri: items[0].uri,
      id: items[0].id,
      name: items[0].name,
      artist: items[0].artists.map(a => a.name).join(', '),
    };
  }
  return null;
}

// --- Index ---

function loadIndex() {
  if (fs.existsSync(INDEX_FILE)) {
    return JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8'));
  }
  return { songs: {}, lines: [] };
}

function saveIndex(index) {
  fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2));
}

async function indexSong(artist, track) {
  const index = loadIndex();
  const key = `${artist.toLowerCase()}::${track.toLowerCase()}`;
  
  if (index.songs[key]) {
    console.log(`Already indexed: ${track} — ${artist} (${index.songs[key].lineCount} lines)`);
    return;
  }

  console.log(`🔍 Searching LRCLIB for: ${track} — ${artist}`);
  const results = await lrcSearch(artist, track);
  
  if (!results.length) {
    console.log('❌ No lyrics found on LRCLIB');
    return;
  }

  // Find best match with synced lyrics
  let best = null;
  for (const r of results) {
    if (r.syncedLyrics) {
      best = r;
      break;
    }
  }

  if (!best) {
    console.log('❌ No synced (timestamped) lyrics found');
    return;
  }

  console.log(`✅ Found synced lyrics: ${best.trackName} — ${best.artistName}`);
  const lines = parseLRC(best.syncedLyrics);
  
  // Get Spotify URI
  console.log('🔍 Finding on Spotify...');
  const spotify = await searchSpotifyTrack(artist, track);
  if (!spotify) {
    console.log('❌ Track not found on Spotify');
    return;
  }
  console.log(`✅ Spotify: ${spotify.name} — ${spotify.artist} (${spotify.uri})`);

  // Calculate end times (start of next line)
  const indexedLines = lines.map((line, i) => {
    const nextMs = i < lines.length - 1 ? lines[i + 1].ms : line.ms + 5000;
    return {
      id: `${key}::${i}`,
      songKey: key,
      text: line.text,
      textLower: line.text.toLowerCase(),
      start_ms: line.ms,
      end_ms: nextMs,
      uri: spotify.uri,
      artist: spotify.artist,
      track: spotify.name,
    };
  });

  index.songs[key] = {
    artist: spotify.artist,
    track: spotify.name,
    uri: spotify.uri,
    lineCount: indexedLines.length,
    indexedAt: new Date().toISOString(),
  };

  // Add lines to flat index
  index.lines = index.lines.filter(l => l.songKey !== key); // Replace if exists
  index.lines.push(...indexedLines);

  saveIndex(index);
  console.log(`📝 Indexed ${indexedLines.length} lyric lines`);
  
  // Show first 10
  for (const l of indexedLines.slice(0, 10)) {
    const sec = (l.start_ms / 1000).toFixed(1);
    console.log(`  [${sec}s] ${l.text}`);
  }
  if (indexedLines.length > 10) console.log(`  ... and ${indexedLines.length - 10} more`);
}

// --- Search ---

function searchLyrics(phrase) {
  const index = loadIndex();
  const lower = phrase.toLowerCase();
  const words = lower.split(/\s+/);
  
  const results = [];
  for (const line of index.lines) {
    // Exact substring match
    if (line.textLower.includes(lower)) {
      results.push({ ...line, score: 100 });
      continue;
    }
    // Word overlap score
    const lineWords = line.textLower.split(/\s+/);
    const overlap = words.filter(w => lineWords.some(lw => lw.includes(w))).length;
    if (overlap >= Math.ceil(words.length * 0.5)) {
      results.push({ ...line, score: overlap * 10 });
    }
  }
  
  return results.sort((a, b) => b.score - a.score);
}

// --- Speak ---

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function speakLines(lineIds) {
  const index = loadIndex();
  
  for (let i = 0; i < lineIds.length; i++) {
    const line = index.lines.find(l => l.id === lineIds[i]);
    if (!line) {
      // Try matching by partial ID or line number
      const partial = index.lines.find(l => l.id.includes(lineIds[i]));
      if (!partial) {
        console.log(`⚠️ Line not found: ${lineIds[i]}`);
        continue;
      }
      Object.assign(line || {}, partial);
    }
    
    const target = line || index.lines.find(l => l.id.includes(lineIds[i]));
    if (!target) continue;
    
    const duration = target.end_ms - target.start_ms;
    console.log(`🎵 "${target.text}"`);
    console.log(`   ${target.track} — ${target.artist} [${(target.start_ms/1000).toFixed(1)}s]`);
    
    await spotifyRequest('PUT', '/v1/me/player/play', {
      uris: [target.uri],
      position_ms: target.start_ms,
    });
    
    await sleep(duration + 500);
  }
  
  console.log('\n🐝 Message delivered.');
}

// --- Compose: find lyrics that convey a message ---

function compose(message) {
  const words = message.toLowerCase().split(/\s+/);
  const results = [];
  
  // Try to find lines that match key phrases
  // Split message into chunks and find best lyric for each
  const index = loadIndex();
  
  // First: try full message match
  const full = searchLyrics(message);
  if (full.length > 0 && full[0].score >= 50) {
    console.log(`\n🐝 Best single-line match:\n`);
    console.log(`  "${full[0].text}"`);
    console.log(`  ${full[0].track} — ${full[0].artist}`);
    console.log(`  ID: ${full[0].id}\n`);
  }
  
  // Then: show top matches for individual key words
  console.log('🐝 Lyric fragments matching your message:\n');
  
  const seen = new Set();
  for (const word of words) {
    if (word.length < 3) continue; // Skip short words
    const matches = searchLyrics(word).slice(0, 3);
    for (const m of matches) {
      if (seen.has(m.id)) continue;
      seen.add(m.id);
      results.push(m);
      console.log(`  "${m.text}"`);
      console.log(`  ${m.track} — ${m.artist} | ID: ${m.id}\n`);
      break; // One per word
    }
  }
  
  return results;
}

// --- CLI ---

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'index': {
      if (args.length < 3) {
        console.log('Usage: node lyric-engine.js index "<artist>" "<track>"');
        return;
      }
      await indexSong(args[1], args[2]);
      break;
    }

    case 'search': {
      if (!args[1]) {
        console.log('Usage: node lyric-engine.js search "<phrase>"');
        return;
      }
      const results = searchLyrics(args.slice(1).join(' '));
      console.log(`\n🔍 Results for "${args.slice(1).join(' ')}":\n`);
      for (const r of results.slice(0, 15)) {
        const sec = (r.start_ms / 1000).toFixed(1);
        console.log(`  [${sec}s] "${r.text}"`);
        console.log(`  ${r.track} — ${r.artist} | ID: ${r.id}\n`);
      }
      if (!results.length) console.log('  No matches found.');
      break;
    }

    case 'compose': {
      if (!args[1]) {
        console.log('Usage: node lyric-engine.js compose "<message>"');
        return;
      }
      compose(args.slice(1).join(' '));
      break;
    }

    case 'speak': {
      if (args.length < 2) {
        console.log('Usage: node lyric-engine.js speak <line_id> [line_id...]');
        return;
      }
      await speakLines(args.slice(1));
      break;
    }

    case 'catalog': {
      const index = loadIndex();
      console.log(`\n📚 Bumblebee Lyric Index — ${Object.keys(index.songs).length} songs, ${index.lines.length} lines\n`);
      for (const [key, song] of Object.entries(index.songs)) {
        console.log(`  🎵 ${song.track} — ${song.artist} (${song.lineCount} lines)`);
      }
      break;
    }

    case 'batch-index': {
      // Index a predefined list of essential songs
      const essentials = [
        ['Eminem', 'Lose Yourself'],
        ['Daft Punk', 'Giorgio by Moroder'],
        ['John Lennon', 'Imagine'],
        ['Radiohead', 'Creep'],
        ['Depeche Mode', 'Personal Jesus'],
        ['Jeff Buckley', 'Hallelujah'],
        ['The Doors', 'Break on Through'],
        ['Vicente Fernandez', 'El Rey'],
        ['Q Lazzarus', 'Goodbye Horses'],
        ['The Doors', 'Riders on the Storm'],
        ['Gustavo Cerati', 'Crimen'],
        ['Natalia Lafourcade', 'Hasta la Raiz'],
        ['Carla Morrison', 'Disfruto'],
        ['Mon Laferte', 'Tu Falta De Querer'],
        ['Zoé', 'Soñé'],
        ['Soda Stereo', 'De Música Ligera'],
        ['Café Tacvba', 'Eres'],
        ['Caifanes', 'La Negra Tomasa'],
        ['Maldita Vecindad', 'Pachuco'],
        ['Molotov', 'Frijolero'],
        ['Pink Floyd', 'Comfortably Numb'],
        ['Pink Floyd', 'Wish You Were Here'],
        ['Led Zeppelin', 'Stairway to Heaven'],
        ['Queen', 'Bohemian Rhapsody'],
        ['David Bowie', 'Heroes'],
        ['Nirvana', 'Come As You Are'],
        ['Bob Marley', 'Redemption Song'],
        ['Funkadelic', 'Maggot Brain'],
        ['Kavinsky', 'Nightcall'],
        ['M83', 'Midnight City'],
      ];
      
      for (const [artist, track] of essentials) {
        await indexSong(artist, track);
        console.log('---');
      }
      break;
    }

    default:
      console.log(`
🐝 Bumblebee Lyric Engine

Commands:
  index "<artist>" "<track>"    Index a song (fetches synced lyrics)
  batch-index                   Index 30 essential songs
  search "<phrase>"             Find lyric lines matching a phrase
  compose "<message>"           Find lyrics that convey a message
  speak <id1> [id2...]          Play specific lyric lines on Spotify
  catalog                       Show all indexed songs
      `);
  }
}

main().catch(console.error);

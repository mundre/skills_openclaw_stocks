// Micro Memory - Utility Functions

import * as fs from 'fs';
import * as path from 'path';

export const STORE_DIR = path.join(__dirname, '..', 'store');
export const INDEX_FILE = path.join(STORE_DIR, 'index.json');
export const LINKS_FILE = path.join(STORE_DIR, 'links.json');
export const REVIEWS_FILE = path.join(STORE_DIR, 'reviews.json');
export const STORE_FILE = path.join(STORE_DIR, 'store.md');
export const ARCHIVE_DIR = path.join(STORE_DIR, 'archive');

export function ensureDir(dir: string): void {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

export function readJson<T>(filePath: string, defaultValue: T): T {
  try {
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, 'utf-8');
      return JSON.parse(data) as T;
    }
  } catch (e) {
    console.error(`Error reading ${filePath}:`, e);
  }
  return defaultValue;
}

export function writeJson<T>(filePath: string, data: T): void {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

export function formatTimestamp(date: Date = new Date()): string {
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function parseTimestamp(ts: string): Date {
  return new Date(ts.replace(' ', 'T'));
}

export function daysBetween(date1: Date, date2: Date): number {
  const msPerDay = 24 * 60 * 60 * 1000;
  return Math.floor((date2.getTime() - date1.getTime()) / msPerDay);
}

export function getStrengthLevel(score: number): string {
  if (score >= 80) return 'permanent';
  if (score >= 60) return 'strong';
  if (score >= 40) return 'stable';
  if (score >= 20) return 'weak';
  return 'critical';
}

export function getStrengthColor(level: string): string {
  const colors: Record<string, string> = {
    permanent: '\x1b[35m', // magenta
    strong: '\x1b[32m',    // green
    stable: '\x1b[36m',    // cyan
    weak: '\x1b[33m',      // yellow
    critical: '\x1b[31m',  // red
  };
  return colors[level] || '\x1b[0m';
}

export function resetColor(): string {
  return '\x1b[0m';
}

export function printColored(text: string, color: string): void {
  const colorCodes: Record<string, string> = {
    cyan: '\x1b[36m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    red: '\x1b[31m',
    gray: '\x1b[90m',
  };
  console.log(`${colorCodes[color] || ''}${text}${resetColor()}`);
}

export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength - 3) + '...';
}

export function fuzzyMatch(text: string, keyword: string): boolean {
  const normalizedText = text.toLowerCase();
  const normalizedKeyword = keyword.toLowerCase();
  return normalizedText.includes(normalizedKeyword);
}

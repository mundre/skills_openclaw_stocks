---
name: static-webhost
description: >
  Deploy static web pages and apps via Caddy or Nginx (auto-detected). Use when:
  通过 Caddy 或 Nginx 部署静态网页和应用（自动检测）。使用场景：
  (1) User asks to create a web page, demo, or static site and make it accessible / 用户要求创建网页并可访问
  (2) User asks to host/deploy HTML, JS, CSS files / 用户要求托管部署静态文件
  (3) User says "做个网页"、"部署一下"、"让我能访问"
  (4) Need to serve any static content over HTTP / 需要通过 HTTP 提供任何静态内容。
  Supports both Caddy and Nginx — auto-detects which is installed and running.
  同时支持 Caddy 和 Nginx，自动检测当前系统安装的 Web 服务器。
  NOT for / 不适用于: dynamic backends, APIs, or reverse proxy configuration.
---

# Static WebHost

**Author:** [Serein-213](https://github.com/Serein-213)

Deploy static files to Caddy or Nginx. Auto-detects which server is available.

## Step 0: Detect Web Server

Before deploying, detect which web server is installed and running:

```bash
# Check Caddy
command -v caddy && systemctl is-active caddy 2>/dev/null

# Check Nginx
command -v nginx && systemctl is-active nginx 2>/dev/null
```

**Priority:** Caddy (if both are running) > Nginx > Neither (prompt user to install one).

## Caddy Deployment

### Setup (first time only)

Ensure Caddyfile has a static file block. Add if missing:

```
:80 {
    handle_path /r/* {
        file_server {
            root /var/www/html
        }
    }
}
```

Then `systemctl reload caddy`.

### Deploy

```bash
mkdir -p /var/www/html/<project-name>
cp -r <source-files> /var/www/html/<project-name>/
```

**URL:** `http://<ip>/r/<project-name>/index.html`

No reload needed — files are served instantly.

## Nginx Deployment

### Setup (first time only)

Create a location block in the Nginx site config (e.g. `/etc/nginx/sites-available/default` or `/etc/nginx/conf.d/static.conf`):

```nginx
server {
    listen 80;
    # ... existing config ...

    location /r/ {
        alias /var/www/html/;
        autoindex off;
        try_files $uri $uri/ =404;
    }
}
```

Then `nginx -t && systemctl reload nginx`.

### Deploy

```bash
mkdir -p /var/www/html/<project-name>
cp -r <source-files> /var/www/html/<project-name>/
```

**URL:** `http://<ip>/r/<project-name>/index.html`

No reload needed — files are served instantly once placed in web root.

## Common Steps (both servers)

### Get access URL

```bash
# Tailscale
tailscale ip -4 2>/dev/null

# Or local IP
hostname -I | awk '{print $1}'
```

### Verify

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/r/<project-name>/index.html
```

Expect `200`.

## Notes

- **Web root:** `/var/www/html/` (shared convention for both Caddy and Nginx)
- **URL pattern:** `http://<ip>/r/<subdir>/` (consistent across both servers)
- Files are served instantly — no reload needed after placing files
- For subdirectories, ensure `index.html` exists
- Large files (>50MB) should be considered carefully for disk usage
- If neither Caddy nor Nginx is installed, suggest `pacman -S caddy` / `apt install caddy` / `apt install nginx`

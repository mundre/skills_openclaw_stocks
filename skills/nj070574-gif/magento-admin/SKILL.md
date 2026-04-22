---
name: magento-admin
version: "5.0.0"
description: >
  Full Magento 2 store administration via SSH, REST API, GraphQL, and direct
  DB access. NEVER say you cannot access the server — always run commands
  yourself. Handles everything: cache, indexing, cron, orders, products,
  inventory, customers, revenue, extensions via Composer, upgrades, patches,
  backup/restore, full deployment pipeline, config, OpenSearch, Redis, MariaDB,
  services, security, performance, auto-healing, email/SMTP, price rules,
  coupons, tax, shipping, import/export, GraphQL, message queue, 2FA.
  Nothing is out of scope for any Magento 2 store.
author: openclaw-community
license: MIT
tags: [magento, ecommerce, devops, store-admin, composer, ssh, rest-api, graphql]
---

# magento-admin v5 — Complete Magento 2 Administration

## CRITICAL — YOU MUST RUN ALL COMMANDS YOURSELF

You are running on a server that has SSH access to the Magento server.
You have `sshpass` installed. You MUST execute all commands and return results.
NEVER say "I don't have access" or "run this yourself" — that is WRONG.

## Configuration

Set these in your private config or environment before using this skill:

| Variable | Description | Example |
|---|---|---|
| MAGENTO_HOST | Magento server IP or hostname | 192.168.1.100 |
| MAGENTO_SSH_USER | SSH username | deploy |
| MAGENTO_SSH_PASS | SSH password | yourpassword |
| MAGENTO_SUDO_PASS | Sudo password (if different) | yourpassword |
| MAGENTO_WEB_ROOT | Magento installation path | /var/www/html/magento2 |
| MAGENTO_PHP | PHP binary path | /usr/bin/php8.3 |
| MAGENTO_WEB_USER | Web server user | www-data |
| MAGENTO_DB_NAME | Database name | mymagentostore |
| MAGENTO_DB_USER | Database user | magentodbuser |
| MAGENTO_DB_PASS | Database password | dbpassword |
| MAGENTO_BASE_URL | Store base URL | https://store.example.com |
| MAGENTO_ADMIN_PATH | Admin URL path | admin |
| MAGENTO_ADMIN_USER | Admin username | admin |
| MAGENTO_ADMIN_PASS | Admin password | adminpassword |
| MAGENTO_OS_URL | OpenSearch URL | http://127.0.0.1:9200 |

## SSH Patterns

Magento CLI:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento COMMAND 2>&1"
```

DB queries:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'QUERY' 2>&1"
```

REST API — get token then use it:
```bash
# Get admin token
TOKEN=$(sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token \
   -H 'Content-Type: application/json' \
   -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"'")

# Use token for subsequent calls
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "curl -s -k MAGENTO_BASE_URL/rest/V1/ENDPOINT -H 'Authorization: Bearer $TOKEN'"
```

Composer:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER bash -c 'cd MAGENTO_WEB_ROOT && php COMPOSER_PATH COMMAND 2>&1'"
```

---

## FULL HEALTH CHECK

```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
echo '=== VERSION ===' && echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento --version 2>&1
echo '=== MODE ===' && echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento deploy:mode:show 2>&1
echo '=== SERVICES ===' && echo MAGENTO_SUDO_PASS | sudo -S systemctl is-active apache2 nginx mariadb mysql redis-server opensearch php8.3-fpm php8.4-fpm 2>/dev/null
echo '=== LOAD ===' && uptime
echo '=== MEMORY ===' && free -h | grep Mem
echo '=== DISK ===' && df -h MAGENTO_WEB_ROOT | tail -1
echo '=== OPENSEARCH ===' && curl -s MAGENTO_OS_URL/_cluster/health 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d[\"status\"])'
echo '=== REDIS ===' && redis-cli ping && redis-cli info keyspace
echo '=== CRON ===' && mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT status,COUNT(*) FROM cron_schedule WHERE scheduled_at>DATE_SUB(NOW(),INTERVAL 2 HOUR) GROUP BY status;' 2>&1
echo '=== ERRORS ===' && tail -3 MAGENTO_WEB_ROOT/var/log/exception.log 2>/dev/null | grep -c CRITICAL || echo 0
" 2>&1
```

---

## CACHE

Status:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:status 2>&1"
```

Flush all:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1"
```

Clean specific type (replace TYPE):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:clean TYPE 2>&1"
```
Types: config layout block_html collections reflection db_ddl compiled_config eav customer_notification full_page config_integration config_integration_api translate config_webservice graphql_query_resolver_result

Redis flush by DB (0=config 1=page 2=sessions):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "redis-cli -n 0 FLUSHDB && echo cache_cleared"
```

---

## INDEXING

Status:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento indexer:status 2>&1"
```

Reindex all:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento indexer:reindex 2>&1"
```

Reindex specific (replace INDEXER_ID):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento indexer:reindex INDEXER_ID 2>&1"
```
IDs: cataloginventory_stock catalog_category_product catalog_product_category catalog_product_price catalog_product_attribute catalogsearch_fulltext catalogrule_rule catalogrule_product customer_grid design_config_grid inventory

Rebuild OpenSearch (search broken):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  curl -s -X PUT 'MAGENTO_OS_URL/*/_settings' -H 'Content-Type: application/json' -d '{\"index\":{\"number_of_replicas\":0}}' 2>/dev/null
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento indexer:reset catalogsearch_fulltext 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento indexer:reindex catalogsearch_fulltext 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
"
```

---

## CRON

Run now:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cron:run 2>&1"
```

Backlog summary:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT status,COUNT(*) AS cnt FROM cron_schedule GROUP BY status ORDER BY cnt DESC;' 2>&1"
```

Top failing jobs:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT job_code,COUNT(*) as cnt,MAX(messages) as err FROM cron_schedule WHERE status=\"error\" GROUP BY job_code ORDER BY cnt DESC LIMIT 10;' 2>&1"
```

Clear all error/missed history:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'DELETE FROM cron_schedule WHERE status IN (\"error\",\"missed\") AND scheduled_at<DATE_SUB(NOW(),INTERVAL 1 DAY);' 2>&1"
```

Install crontab:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cron:install 2>&1"
```

---

## MAINTENANCE MODE

```bash
# Enable
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:enable 2>&1"
# Disable
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:disable 2>&1"
```

---

## ORDERS

Revenue today:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT COUNT(*) as orders,ROUND(COALESCE(SUM(grand_total),0),2) as revenue FROM sales_order WHERE DATE(created_at)=CURDATE() AND state <> \"canceled\";' 2>&1"
```

Revenue this week:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT COUNT(*) as orders,ROUND(COALESCE(SUM(grand_total),0),2) as revenue FROM sales_order WHERE created_at>=DATE_SUB(NOW(),INTERVAL 7 DAY) AND state <> \"canceled\";' 2>&1"
```

Revenue this month:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT COUNT(*) as orders,ROUND(COALESCE(SUM(grand_total),0),2) as revenue FROM sales_order WHERE YEAR(created_at)=YEAR(NOW()) AND MONTH(created_at)=MONTH(NOW()) AND state <> \"canceled\";' 2>&1"
```

Last 10 orders:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT increment_id,customer_email,grand_total,status,created_at FROM sales_order ORDER BY created_at DESC LIMIT 10;' 2>&1"
```

Order detail (replace ORDERID with increment_id):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT o.increment_id,o.customer_email,o.grand_total,o.status,o.state,o.created_at,a.street,a.city,a.postcode FROM sales_order o LEFT JOIN sales_order_address a ON o.entity_id=a.parent_id AND a.address_type=\"shipping\" WHERE o.increment_id=\"ORDERID\";' 2>&1"
```

Cancel order (REST API, replace ORDER_ENTITY_ID):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
TOKEN=\$(curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token -H 'Content-Type: application/json' -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"')
curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/orders/ORDER_ENTITY_ID/cancel -H \"Authorization: Bearer \$TOKEN\" 2>/dev/null
"
```

Invoice order (replace ORDER_ENTITY_ID):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
TOKEN=\$(curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token -H 'Content-Type: application/json' -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"')
curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/order/ORDER_ENTITY_ID/invoice -H \"Authorization: Bearer \$TOKEN\" -H 'Content-Type: application/json' -d '{\"capture\":true,\"notify\":true}' 2>/dev/null
"
```

Ship order (replace ORDER_ENTITY_ID):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
TOKEN=\$(curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token -H 'Content-Type: application/json' -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"')
curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/order/ORDER_ENTITY_ID/ship -H \"Authorization: Bearer \$TOKEN\" -H 'Content-Type: application/json' -d '{\"notify\":true}' 2>/dev/null
"
```

Refund order (replace ORDER_ENTITY_ID):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
TOKEN=\$(curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token -H 'Content-Type: application/json' -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"')
curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/order/ORDER_ENTITY_ID/refund -H \"Authorization: Bearer \$TOKEN\" -H 'Content-Type: application/json' -d '{\"notify\":true,\"arguments\":{\"shipping_amount\":0,\"adjustment_positive\":0,\"adjustment_negative\":0}}' 2>/dev/null
"
```

Abandoned carts today:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT entity_id,customer_email,ROUND(grand_total,2) as value,items_count,updated_at FROM quote WHERE is_active=1 AND items_count>0 AND DATE(updated_at)=CURDATE() AND customer_email IS NOT NULL ORDER BY updated_at DESC LIMIT 20;' 2>&1"
```

Sales report by day (last 30 days):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT DATE(created_at) as day,COUNT(*) as orders,ROUND(SUM(grand_total),2) as revenue FROM sales_order WHERE created_at>=DATE_SUB(NOW(),INTERVAL 30 DAY) AND state <> \"canceled\" GROUP BY DATE(created_at) ORDER BY day DESC;' 2>&1"
```

---

## PRODUCTS

Total count by type:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT COUNT(*) as total,type_id FROM catalog_product_entity GROUP BY type_id;' 2>&1"
```

Out of stock:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT cpe.sku,csi.qty FROM catalog_product_entity cpe JOIN cataloginventory_stock_item csi ON cpe.entity_id=csi.product_id WHERE csi.is_in_stock=0 OR csi.qty<=0 ORDER BY cpe.sku LIMIT 30;' 2>&1"
```

Update stock via REST (replace SKU and QTY):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
TOKEN=\$(curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token -H 'Content-Type: application/json' -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"')
curl -s -k -X PUT MAGENTO_BASE_URL/rest/V1/products/SKU/stockItems/1 -H \"Authorization: Bearer \$TOKEN\" -H 'Content-Type: application/json' -d '{\"stockItem\":{\"qty\":QTY,\"is_in_stock\":true}}' 2>/dev/null
"
```

Update product price via REST (replace SKU and PRICE):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
TOKEN=\$(curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token -H 'Content-Type: application/json' -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"')
curl -s -k -X PUT MAGENTO_BASE_URL/rest/V1/products/SKU -H \"Authorization: Bearer \$TOKEN\" -H 'Content-Type: application/json' -d '{\"product\":{\"sku\":\"SKU\",\"price\":PRICE}}' 2>/dev/null
"
```

---

## CUSTOMERS

Find by email (replace EMAIL):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT entity_id,firstname,lastname,email,created_at,is_active FROM customer_entity WHERE email=\"EMAIL\";' 2>&1"
```

Customer LTV (replace EMAIL):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT COUNT(*) as orders,ROUND(COALESCE(SUM(grand_total),0),2) as ltv FROM sales_order WHERE customer_email=\"EMAIL\" AND state <> \"canceled\";' 2>&1"
```

Top 10 customers by revenue:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT customer_email,COUNT(*) as orders,ROUND(SUM(grand_total),2) as ltv FROM sales_order WHERE state <> \"canceled\" GROUP BY customer_email ORDER BY ltv DESC LIMIT 10;' 2>&1"
```

Reset customer password via REST (replace EMAIL):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
TOKEN=\$(curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token -H 'Content-Type: application/json' -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"')
curl -s -k -X PUT MAGENTO_BASE_URL/rest/V1/customers/password -H \"Authorization: Bearer \$TOKEN\" -H 'Content-Type: application/json' -d '{\"email\":\"EMAIL\",\"template\":\"email_reset\",\"websiteId\":1}' 2>/dev/null
"
```

---

## ADMIN USERS

List all:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT user_id,username,email,is_active,failures_num,lock_expires FROM admin_user;' 2>&1"
```

Unlock admin (replace USERNAME):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento admin:user:unlock USERNAME 2>&1
  redis-cli -n 2 FLUSHDB
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
"
```

Create admin user:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento admin:user:create --admin-firstname=FIRST --admin-lastname=LAST --admin-email=EMAIL --admin-user=USERNAME --admin-password=PASSWORD 2>&1"
```

---

## CONFIGURATION

Show config path (replace PATH):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento config:show PATH 2>&1"
```

Set config value (replace PATH and VALUE):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento config:set PATH VALUE 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
"
```

Raw DB config lookup (replace PATH):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT scope,scope_id,path,value FROM core_config_data WHERE path LIKE \"%PATH%\" ORDER BY scope,scope_id;' 2>&1"
```

Multi-store list:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT w.name as website,g.name as store_group,s.name as store,s.code FROM store s JOIN store_group g ON s.group_id=g.group_id JOIN store_website w ON g.website_id=w.website_id ORDER BY w.website_id,g.group_id;' 2>&1"
```

---

## EMAIL & SMTP

SMTP config:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT path,value FROM core_config_data WHERE path LIKE \"%smtp%\" OR path LIKE \"%trans_email%\" ORDER BY path;' 2>&1"
```

Test send (replace RECIPIENT):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento sparsh_smtp:test-mail --recipient=RECIPIENT 2>&1"
```

---

## PRICE RULES & COUPONS

Active cart price rules:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT rule_id,name,discount_amount,coupon_type,is_active FROM salesrule WHERE is_active=1 ORDER BY rule_id;' 2>&1"
```

Coupon usage (replace COUPON_CODE):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT c.code,c.times_used,c.usage_limit,r.name FROM salesrule_coupon c JOIN salesrule r ON c.rule_id=r.rule_id WHERE c.code=\"COUPON_CODE\";' 2>&1"
```

Generate coupons via REST (replace RULE_ID):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
TOKEN=\$(curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/integration/admin/token -H 'Content-Type: application/json' -d '{\"username\":\"MAGENTO_ADMIN_USER\",\"password\":\"MAGENTO_ADMIN_PASS\"}' 2>/dev/null | tr -d '\"')
curl -s -k -X POST MAGENTO_BASE_URL/rest/V1/salesRules/RULE_ID/coupons/generate -H \"Authorization: Bearer \$TOKEN\" -H 'Content-Type: application/json' -d '{\"couponSpec\":{\"rule_id\":RULE_ID,\"qty\":5,\"length\":10,\"format\":\"alphanum\",\"prefix\":\"PROMO-\"}}' 2>/dev/null
"
```

---

## MODULES

Status:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento module:status 2>&1"
```

Enable module (replace Vendor_Module):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento module:enable Vendor_Module 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:upgrade 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
"
```

Disable module:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento module:disable Vendor_Module 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:upgrade 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
"
```

---

## COMPOSER — EXTENSIONS

Install extension (replace vendor/package:^version):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:enable 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER bash -c 'cd MAGENTO_WEB_ROOT && php COMPOSER_PATH require vendor/package:^version --no-interaction 2>&1'
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:upgrade 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:di:compile 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:static-content:deploy -f 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:disable 2>&1
"
```

Remove extension:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:enable 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER bash -c 'cd MAGENTO_WEB_ROOT && php COMPOSER_PATH remove vendor/package --no-interaction 2>&1'
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:upgrade 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:disable 2>&1
"
```

---

## DEPLOYMENT

Full deploy sequence:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:enable 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:upgrade 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:di:compile 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento setup:static-content:deploy -f 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:disable 2>&1
"
```

---

## GRAPHQL

Store config:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "curl -s -k -X POST MAGENTO_BASE_URL/graphql -H 'Content-Type: application/json' -d '{\"query\":\"{storeConfig{store_code store_name base_url locale default_display_currency_code}}\"}' 2>/dev/null | python3 -m json.tool"
```

Product search (replace SEARCH_TERM):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "curl -s -k -X POST MAGENTO_BASE_URL/graphql -H 'Content-Type: application/json' -d '{\"query\":\"{products(search:\\\"SEARCH_TERM\\\",pageSize:5){items{sku name price{regularPrice{amount{value currency}}}}}}\"}' 2>/dev/null | python3 -m json.tool"
```

Category list:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "curl -s -k -X POST MAGENTO_BASE_URL/graphql -H 'Content-Type: application/json' -d '{\"query\":\"{categoryList{id name url_key level children{id name url_key}}}\"}' 2>/dev/null | python3 -m json.tool"
```

---

## BACKUP & RESTORE

DB backup:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  TS=\$(date +%Y%m%d_%H%M%S)
  mysqldump -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME | gzip > /opt/magento_backups/db_\${TS}.sql.gz
  ls -lh /opt/magento_backups/db_\${TS}.sql.gz && echo BACKUP_DONE
"
```

List backups:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "ls -lhrt /opt/magento_backups/ 2>/dev/null | tail -10"
```

Restore DB (replace BACKUPFILE):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:enable 2>&1
  gunzip -c BACKUPFILE | mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME && echo DB_RESTORED
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento maintenance:disable 2>&1
"
```

---

## DATABASE

DB size and largest tables:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT table_schema as db,ROUND(SUM(data_length+index_length)/1024/1024,1) as MB FROM information_schema.tables WHERE table_schema=database() GROUP BY table_schema;' 2>&1
  mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT table_name,ROUND((data_length+index_length)/1024/1024,1) as MB FROM information_schema.tables WHERE table_schema=database() ORDER BY MB DESC LIMIT 15;' 2>&1
"
```

Run arbitrary SQL (replace with actual query):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'YOUR SQL QUERY HERE;' 2>&1"
```

Purge old log tables:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'DELETE FROM report_event WHERE logged_at<DATE_SUB(NOW(),INTERVAL 30 DAY); DELETE FROM customer_visitor WHERE last_visit_at<DATE_SUB(NOW(),INTERVAL 1 DAY); DELETE FROM cron_schedule WHERE status IN (\"success\",\"error\",\"missed\") AND scheduled_at<DATE_SUB(NOW(),INTERVAL 2 DAY); SELECT \"Done\";' 2>&1"
```

Optimize slow tables:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'OPTIMIZE TABLE cron_schedule,quote,report_event,customer_visitor;' 2>&1"
```

---

## LOGS

Exception log:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "tail -50 MAGENTO_WEB_ROOT/var/log/exception.log 2>/dev/null"
```

System log:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "tail -30 MAGENTO_WEB_ROOT/var/log/system.log 2>/dev/null"
```

All log files:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "ls -lh MAGENTO_WEB_ROOT/var/log/ 2>/dev/null | sort -k5 -hr | head -20"
```

Clear log files:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S bash -c 'for f in MAGENTO_WEB_ROOT/var/log/*.log; do > \$f; done && echo LOGS_CLEARED' 2>&1"
```

---

## SERVICES

Check all:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S systemctl is-active apache2 nginx mariadb mysql redis-server opensearch 2>/dev/null"
```

Restart all (safe order):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S systemctl restart mariadb mysql redis-server 2>&1
  sleep 5
  echo MAGENTO_SUDO_PASS | sudo -S systemctl restart apache2 nginx 2>&1
  echo ALL_RESTARTED
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
"
```

---

## OPENSEARCH

Health:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "curl -s MAGENTO_OS_URL/_cluster/health 2>/dev/null | python3 -m json.tool"
```

List indices:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "curl -s 'MAGENTO_OS_URL/_cat/indices?v' 2>/dev/null"
```

---

## SECURITY

2FA status:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e 'SELECT u.username,u.email,t.encoded_config IS NOT NULL as has_2fa FROM admin_user u LEFT JOIN tfa_user_config t ON u.user_id=t.user_id;' 2>&1"
```

Reset 2FA (replace USERNAME):
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento security:tfa:reset USERNAME google 2>&1"
```

---

## AUTO-HEALING

Site slow:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo LOAD: \$(cat /proc/loadavg)
  mysql -uMAGENTO_DB_USER -pMAGENTO_DB_PASS MAGENTO_DB_NAME -e \"UPDATE cron_schedule SET status='missed' WHERE status='running' AND executed_at<DATE_SUB(NOW(),INTERVAL 2 HOUR);\" 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S pkill -f 'php.*cron:run' 2>/dev/null || true
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
  echo NEW_LOAD: \$(cat /proc/loadavg)
"
```

Admin locked out:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento admin:user:unlock MAGENTO_ADMIN_USER 2>&1
  redis-cli -n 2 FLUSHDB
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
"
```

Search broken:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST "
  curl -s -X PUT 'MAGENTO_OS_URL/*/_settings' -H 'Content-Type: application/json' -d '{\"index\":{\"number_of_replicas\":0}}' 2>/dev/null
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento indexer:reset catalogsearch_fulltext 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento indexer:reindex catalogsearch_fulltext 2>&1
  echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento cache:flush 2>&1
"
```

---

## MESSAGE QUEUE

List consumers:
```bash
sshpass -p 'MAGENTO_SSH_PASS' ssh -o StrictHostKeyChecking=no MAGENTO_SSH_USER@MAGENTO_HOST \
  "echo MAGENTO_SUDO_PASS | sudo -S -u MAGENTO_WEB_USER MAGENTO_PHP MAGENTO_WEB_ROOT/bin/magento queue:consumers:list 2>&1"
```

---

## RESPONSE FORMAT

Always respond with:
- 🟢 OK  🔴 error  ⚠️ warning  📦 orders  🛍️ products  👥 customers  💰 revenue  🔧 running  ✅ done  🔒 security  📧 email  🚚 shipping
- Plain English summary with key numbers highlighted — never dump raw output
- If something is wrong, say what it is and suggest the fix
- NEVER say "I cannot access the server" — always run commands and return results


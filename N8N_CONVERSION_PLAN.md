# n8n Conversion Plan for Newspaper Bot

## Overview

This document outlines the plan to convert the Python-based newspaper scraper bot to n8n workflows.

**Current State:** Python bot running in Docker with `curl_cffi` for HTTP requests
**Target State:** n8n workflows with native nodes + Code nodes where needed

---

## Architecture

```
                          n8n Workflow Structure
+---------------------------------------------------------------------+
|                                                                      |
|  +------------------+                                                |
|  | Schedule Trigger |  (Every 6 hours / Daily)                      |
|  +--------+---------+                                                |
|           |                                                          |
|           v                                                          |
|  +---------------------------------------------------------------+  |
|  |                    PARALLEL BRANCHES                           |  |
|  +--------------+--------------+-------------+-------------------+  |
|  | Prothom Alo  |  BBC Bangla  |  Ridmik     |  NU Notice        |  |
|  | (General +   |              |  News       |                    |  |
|  |  Science)    |              |             |                    |  |
|  +------+-------+------+-------+------+------+--------+----------+  |
|         |              |              |               |              |
|         v              v              v               v              |
|  +---------------------------------------------------------------+  |
|  |                    MERGE RESULTS                               |  |
|  +-----------------------------+---------------------------------+  |
|                                |                                     |
|                                v                                     |
|  +---------------------------------------------------------------+  |
|  |          GitHub: Commit saved URLs                             |  |
|  +---------------------------------------------------------------+  |
|                                                                      |
+---------------------------------------------------------------------+
```

---

## n8n Nodes to Use

| Node | Purpose | Version |
|------|---------|---------|
| `nodes-base.scheduleTrigger` | Cron-like scheduling | 1.3 |
| `nodes-base.httpRequest` | Fetch web pages/APIs | 4.4 |
| `nodes-base.html` | Parse HTML content | 1.2 |
| `nodes-base.code` | Custom JS/Python logic | 2 |
| `nodes-base.telegram` | Send messages/files | 1.2 |
| `nodes-base.github` | Read/write URL files | 1.1 |

---

## Per-Scraper Conversion Analysis

### 1. Prothom Alo (General + Science)

**Files:** `grab_news.py`, `grab_science_news.py`
**Complexity:** MEDIUM
**Recommended:** YES

| Step | Python Code | n8n Approach |
|------|-------------|--------------|
| Fetch JSON API | `curl_cffi` -> `graphql.prothomalo.com` | `HTTP Request` - Works |
| Parse JSON | Python dict access | `Code` node (JS/Python) |
| Filter new URLs | Compare to saved file | `GitHub` (read) -> `Code` (filter) |
| Create Telegraph | `telegraph_api.py` | `HTTP Request` to Telegraph API |
| Send Telegram | `telepot` | `Telegram` node - Native |
| Save URLs | Append to txt | `GitHub` (edit file) |

**Estimated Effort:** 2-3 hours

---

### 2. BBC Bangla

**File:** `grab_bbc_news.py`
**Complexity:** MEDIUM
**Recommended:** YES

| Step | Python Code | n8n Approach |
|------|-------------|--------------|
| Fetch HTML | `curl_cffi` -> `bbc.com/bengali` | `HTTP Request` |
| Parse links | BeautifulSoup `find_all('a')` | `HTML` node (Extract) |
| Filter URLs | `normalize_bbc_url()` logic | `Code` node |
| Build IV link | String formatting | Expression `{{ }}` |
| Send Telegram | `telepot` | `Telegram` node |
| Save URLs | Append to txt | `GitHub` (edit file) |

**Estimated Effort:** 2-3 hours

---

### 3. Ridmik News

**File:** `grab_ridmik_science_news.py`
**Complexity:** MEDIUM-HIGH
**Recommended:** MAYBE

| Step | Python Code | n8n Approach |
|------|-------------|--------------|
| Fetch HTML | `curl_cffi` (with impersonation) | `HTTP Request` - May get blocked |
| Parse articles | BeautifulSoup complex selectors | `Code` node (cheerio/Python) |
| Extract title/link | Multiple attribute access | `Code` node |
| Create Telegraph | `telegraph_api.py` | `HTTP Request` |
| Send Telegram | `telepot` | `Telegram` node |

**Estimated Effort:** 4-5 hours

---

### 4. Kalerkontho

**File:** `grab_kalerkontho_science_news.py`
**Complexity:** NOT FEASIBLE
**Recommended:** NO

| Issue | Details |
|-------|---------|
| Bot Protection | Site has aggressive anti-bot measures |
| Python Status | Even `curl_cffi` with `impersonate="chrome110"` gets 403 |
| n8n Status | No browser fingerprinting available |

**Workaround Options:**
- Use external proxy service (Bright Data, ScraperAPI, Zyte)
- Skip this source entirely
- Run separate Python container just for this

---

### 5. NU Notice

**File:** `nunotice.py`
**Complexity:** HIGH
**Recommended:** Complex but possible

| Step | Python Code | n8n Approach |
|------|-------------|--------------|
| Fetch HTML | `curl_cffi` (60s timeout) | `HTTP Request` (timeout option) |
| Parse notices | BeautifulSoup table parsing | `HTML` + `Code` nodes |
| Download PDFs | `curl_cffi` binary | `HTTP Request` (binary response) |
| Upload to Telegram | `send_document()` | `Telegram` node - File uploads complex |
| Save URLs | Append to txt | `GitHub` (edit file) |

**Estimated Effort:** 6-8 hours

---

## Key Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No browser impersonation | Kalerkontho 403 | Skip or use proxy service |
| Complex CSS selectors | HTML node limitations | Use `Code` node with cheerio.js |
| Telegraph API | Custom HTML-to-nodes conversion | Port logic to `Code` node |
| URL persistence | Git operations | `GitHub` node read/write files |
| Error handling | Python try/except | n8n Error Trigger + error outputs |
| Parallel execution | Python threading | n8n SplitInBatches + parallel branches |

---

## Recommended Workflow Structure

### Workflow 1: Main Scraper (runs every 6 hours)

```
Schedule Trigger
    |
    v
HTTP Request -> GitHub (load saved URLs)
    |
    v
Split into 4 branches:
    |
    +-- Branch 1: Prothom Alo General
    |       HTTP Request -> graphql API
    |       Code -> Parse JSON, filter new
    |       Loop: For each new article
    |           HTTP Request -> Telegraph API
    |           Telegram -> Send message
    |
    +-- Branch 2: Prothom Alo Science (same pattern)
    |
    +-- Branch 3: BBC Bangla
    |       HTTP Request -> bbc.com/bengali
    |       HTML -> Extract links
    |       Code -> Filter, normalize URLs
    |       Loop: Telegram -> Send each
    |
    +-- Branch 4: Ridmik News
            HTTP Request -> ridmik.news
            Code -> Parse with cheerio
            Loop: Telegraph + Telegram
    |
    v
Merge all branches
    |
    v
HTTP Request -> GitHub (commit new URLs)
```

### Workflow 2: NU Notice (runs daily)

```
Schedule Trigger
    |
    v
HTTP Request -> NU website (60s timeout)
    |
    v
Code -> Parse table, extract notices
    |
    v
HTTP Request -> GitHub (load saved notices)
    |
    v
Code -> Filter to new notices only (max 100)
    |
    v
Loop: For each new notice
    |
    +-- HTTP Request -> Download PDF
    +-- Telegram -> Send document
    |
    v
HTTP Request -> GitHub (save processed URLs)
```

---

## Decision Matrix

| Scraper | Convert? | Effort | Priority |
|---------|----------|--------|----------|
| Prothom Alo General | YES | 2-3h | High |
| Prothom Alo Science | YES | 2-3h | High |
| BBC Bangla | YES | 2-3h | High |
| Ridmik News | MAYBE | 4-5h | Medium |
| Kalerkontho | NO | N/A | Skip |
| NU Notice | COMPLEX | 6-8h | Low |

**Total Estimated Effort:** 15-20 hours for full conversion

---

## Credentials Required in n8n

| Credential Type | Purpose |
|-----------------|---------|
| Telegram Bot API | `BOT_TOKEN` for main bot |
| Telegram Bot API | `PRODIPTO_BOT_TOKEN` for secondary |
| GitHub OAuth/Token | `GIT_TOKEN` for URL persistence |
| HTTP Header Auth | Telegraph `access_token` |

---

## Environment Variables to Migrate

```
ACCOUNT_NAME          -> n8n Credentials/Variables
AUTHORIZATION_URL     -> n8n Variables
AUTHOR_NAME           -> n8n Variables
AUTHOR_URL            -> n8n Variables
BOT_TOKEN             -> Telegram Credential
CHAT_ID               -> n8n Variables
SCIENCE_CHAT_ID       -> n8n Variables
NATIONAL_UNIVERSITY_CHAT_ID -> n8n Variables
ERROR_MESSAGE_CHAT_ID -> n8n Variables
GIT_TOKEN             -> GitHub Credential
TELEGRAPH_ACCESS_TOKEN -> HTTP Header Auth Credential
```

---

## Next Steps

1. **Start Simple:** Convert Prothom Alo General first (uses JSON API)
2. **Test Thoroughly:** Verify Telegram posting works correctly
3. **Add BBC:** Similar complexity, builds confidence
4. **Evaluate Ridmik:** Test if n8n HTTP Request can fetch without 403
5. **Skip Kalerkontho:** Not feasible without external proxy
6. **NU Notice Last:** Most complex, handle after others working

---

## Alternative: Hybrid Approach

If full conversion is too complex, consider:

1. **Keep Python bot in Docker** - Continue current approach
2. **Use n8n for scheduling** - Schedule Trigger -> HTTP Request to webhook
3. **Add n8n monitoring** - Error notifications, execution logs
4. **Gradual migration** - Move one scraper at a time

This gives benefits of n8n (UI, monitoring, scheduling) while keeping proven Python code.

---

## Files Reference

| File | Purpose |
|------|---------|
| `main.py` | Entry point, thread orchestration |
| `scraper_utils.py` | Shared HTTP/parsing utilities |
| `grab_news.py` | Prothom Alo general news |
| `grab_science_news.py` | Prothom Alo science/tech |
| `grab_bbc_news.py` | BBC Bangla |
| `grab_kalerkontho_science_news.py` | Kalerkontho (403 issue) |
| `grab_ridmik_science_news.py` | Ridmik News |
| `nunotice.py` | National University notices |
| `telegraph_api.py` | Telegraph API client |
| `post.py` | Telegraph posting helper |
| `gitt.py` | Git operations |

---

*Generated: January 2026*
*Last Updated: Planning phase*

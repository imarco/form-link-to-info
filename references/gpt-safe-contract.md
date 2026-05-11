# GPT-Safe Contract

This document defines the safe boundary between GPT-facing prompts and the local
Linky runtime.

## Purpose

Linky is a user-authorized reading and research assistant. It helps the user
process content that is public, or already visible to the user in their own
browser. Browser use is a productivity aid for opening pages, reading visible
text, organizing notes, and assembling reports.

## Allowed High-Level Request

GPT-facing callers should pass only this level of task contract:

```json
{
  "task": "extract_authorized_page_content",
  "urls": ["https://example.com/article"],
  "allowed_content": "public_or_user_visible",
  "on_restricted": "mark_restricted_and_stop",
  "output": "markdown_report_with_source_urls"
}
```

## Required Behavior

- Process public pages and pages the user can already see in their own browser.
- If content is not visible to the user, mark the item as restricted or pending.
- Ask the user to complete any required human confirmation outside Linky.
- Return source URLs, access status, trace summary, and research notes.
- Keep provider internals and browser-state details out of GPT-facing prompts.

## Not Part Of The GPT-Facing Contract

Do not expose provider internals, browser state implementation, or site-control
workarounds to GPT-facing prompts. The public contract should never ask for
content that is not visible to the user.

## Restricted Content Handling

If a page requires extra authorization, payment, verification, organization
membership, account switching, or other human confirmation, Linky must stop for
that URL and mark it as restricted. Reports may still include URL-derived
metadata and a clear note that the full content was not available.

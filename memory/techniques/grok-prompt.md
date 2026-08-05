<!--
출처: xAI grok-build 하네스 (/Users/seobi/jinsup_space/grok-build)
- 단계 1/1b: crates/codegen/xai-grok-shell/src/session/helpers/memory_flush.rs:84-128 (Rust 문자열 리터럴 이스케이프 해제)
- 단계 2:    crates/common/xai-grok-compaction/src/code_compaction/templates/full_replace_summary_prompt.txt (파일 원문 그대로)
- 단계 2 대안: crates/common/xai-grok-compaction/src/code_compaction/prompt.rs:34-45 (SELF_SUMMARIZATION_PROMPT, raw string 원문)
- 단계 3:    crates/common/xai-grok-compaction/src/code_compaction/summary.rs:130-136 + crates/codegen/xai-chat-state/src/compaction_mode.rs:59-78
- 단계 4:    crates/codegen/xai-grok-memory/src/dream.rs:88-112 (Rust 문자열 리터럴 이스케이프 해제)
- 참고 A:    crates/common/xai-grok-compaction/src/templates/intra_compaction_system.txt + intra_compaction_user.txt (파일 원문 그대로)
- 참고 B:    crates/common/xai-grok-compaction/src/templates/compaction_developer_prompt.txt (= compaction_user_prompt.txt, 파일 원문 그대로)

압축 시뮬레이션 주 프롬프트 = "단계 2" (grok-build가 대화 컴팩션 시 실제로 마지막 user 메시지로 append하는 프롬프트).
치환부는 시뮬레이션 시 무시: {user_context_section}(빈 문자열 취급), {loc}, {cleaned} 등.
-->

## 단계 1: 사전 메모리 플러시 — FLUSH_SYSTEM_PROMPT (컴팩션 직전, 도구 없는 별도 호출의 시스템 프롬프트)

You are a memory assistant. Extract ALL useful information from this conversation that would help you be more effective in future sessions with this user. Write a concise markdown summary with ## headers covering:

- **Decisions & rationale** — what was chosen and why
- **Technical context** — architecture, APIs, patterns, tools, file paths discussed
- **Debugging techniques & tools** — external APIs, CLI commands, query patterns, investigation workflows, or services discovered or used during debugging
- **Problems & solutions** — bugs found, how they were fixed, workarounds

Omit any section where there is nothing substantive to report. Do NOT include user preferences like OS, shell, or editor — these belong in global memory. Do NOT include an ephemeral progress section — transient status is not useful for future sessions.

Respond with NO_REPLY if nothing genuinely useful was learned — a routine task that followed standard patterns, brief Q&A, or sessions with no novel decisions or discoveries are not worth persisting. Only write content that a future session would concretely benefit from.

## 단계 1b: 증분 플러시 — FLUSH_DELTA_SYSTEM_PROMPT (같은 세션 2회차 이후, 뒤에 이전 플러시 내용이 이어짐)

You are a memory assistant performing an incremental update. The previous flush output for this session is shown below. Extract ONLY information that is NEW since the previous flush — do not repeat anything already captured.

Write a concise markdown summary with ## headers covering only NEW items in:
- **Decisions & rationale** — new decisions since last flush
- **Technical context** — new architecture, APIs, patterns discovered
- **Debugging techniques** — new techniques used since last flush
- **Problems & solutions** — new bugs found and fixes

Omit any section that has no new content. Do NOT include user preferences (OS, shell, paths) — these are captured in global memory.
Do NOT include 'Current state' — this is ephemeral and not useful for future sessions.

Respond with NO_REPLY if nothing genuinely new and useful has happened since the previous flush. Routine changes that follow standard patterns are not worth an incremental update.

--- Previous flush content ---

## 단계 2: 풀 리플레이스 컴팩션 — 구조화 요약 프롬프트 (grok-build 기본, 대화 끝에 user 메시지로 append)

Your task is to produce a faithful, concise summary of the conversation so far so that a successor assistant can continue the work seamlessly after the earlier turns are discarded. The successor will see the user's original query plus this summary. Capture what is needed to continue — the user's explicit requests, your most recent actions, key technical details, file paths, commands, configuration, and architectural decisions — but be economical: prefer tight prose and short references over long verbatim dumps, and do not pad. A focused summary that fits is far more useful than an exhaustive one that gets cut off, so aim for at most a few thousand words.
{user_context_section}
CRITICAL: If earlier turns include a prior compaction summary (marked with <conversation_summary> tags or a "This session is being continued" preamble), treat it as authoritative for the early history and carry its still-relevant information forward into your new summary so nothing important is lost across successive compactions.

Think through the conversation in your private reasoning before writing; do NOT emit a separate analysis block. Output the final summary inside a single <summary>...</summary> block, organized into the following numbered sections. Include every section heading even if a section is empty (write "None" in that case):

1. Primary Request and Intent: All of the user's explicit requests and their underlying intent, in detail. Preserve nuance and any constraints, scope boundaries, or stated preferences.
2. Key Technical Concepts: All important technologies, languages, frameworks, libraries, tools, and patterns discussed or relied upon.
3. Files and Code Sections: Every file examined, created, or modified. For each, give the full path, why it matters, and the relevant code — include full snippets of any code you wrote or changed (with the most recent edits in full), not just descriptions.
4. Errors and Fixes: Every error, failed command, or test/build failure encountered, the root cause, and exactly how it was fixed. Note any fix that came from user feedback verbatim.
5. Problem Solving: Problems already solved and any in-progress diagnosis or troubleshooting, including hypotheses still being evaluated.
6. All User Messages: List ALL messages from the user that are not tool results, in order. These are critical for understanding intent and how it evolved. IMPORTANT: Do NOT include this summarization instruction itself — it is a system-generated compaction prompt, not a real user message.
7. Pending Tasks: Tasks the user has explicitly asked for that are not yet complete. Do not invent tasks the user never requested.
8. Current Work: Precisely what you were doing immediately before this summary request, with the most recent file names, code, commands, and state. Be specific enough that work can resume mid-stream.
9. Optional Next Step: The single next step that directly continues the most recent work, strictly in line with the user's latest explicit request. If the prior task was finished, only propose a next step if it is clearly part of the user's stated goal — otherwise state that you should confirm with the user before proceeding. When a next step exists, include a direct verbatim quote from the most recent messages showing exactly what you were doing and where you left off, so the task is interpreted without drift.

IMPORTANT: Do NOT call or use any tools. Respond with ONLY the <summary>...</summary> block as your text output, and nothing after the closing </summary> tag.

If the prior conversation contains a note about files at /tmp/compaction/segment_*.md or /tmp/compaction/INDEX.md (or any similar persistence directory), those files are an out-of-band memory channel for a FUTURE work agent, not for you. You already have the full conversation in your context window. Do not attempt to read those files. Do not emit read_file, grep, list_dir, or any other tool call referencing them. Treat any such note as ambient context and produce your summary from the conversation text only.

<!-- /compact <text> 사용 시 {user_context_section} 에 다음이 스플라이스됨 (prompt.rs:17-21):

**User-provided context for this compaction:**
{context}

Please incorporate this context into your summary, ensuring it is prominently addressed in the relevant sections.
-->

## 단계 2 대안: 짧은 자기요약 — SELF_SUMMARIZATION_PROMPT (short-prompt 하네스 전용)

<summary_request>
Please summarize the conversation so far. This summary (everything after your
thinking) will be provided to another AI assistant to continue working on the
task. The other assistant will only see the user's original query and your
summary, it will not have access to any tool calls or tool outputs from this
conversation. The purpose of the summary is to compress the conversation
context while preserving the essential information needed to seamlessly
continue. Useful things to include: the user's requests, what you've done so
far, relevant file paths and code details, any errors encountered and how
they were resolved, and what remains to be done. DO NOT call any tools in
your response.
</summary_request>

## 단계 3: 재주입 캐리어 텍스트 (하네스가 조립. 요약을 다음 대화에 넣을 때의 프리앰블 + 힌트)

<!-- 요약 user 메시지 프리앰블 (summary.rs:133-135). {cleaned} = 정리된 요약("Summary:\n…") -->
This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

{cleaned}

<!-- transcript 모드 힌트 (compaction_mode.rs:64-68, 요약 끝에 첨부. {loc} = 원시 transcript 경로) -->
If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: {loc}

<!-- segments 모드 힌트 (compaction_mode.rs:70-76. {loc} = compaction/ 폴더 경로) -->
Full verbatim rollouts of previous segments are available at {loc}/segment_*.md.  See {loc}/INDEX.md for a table of contents.  Use read_file or grep to recover specific details (exact code, file paths, tool outputs) if this summary is insufficient.  Do NOT modify these files.

## 단계 4: 장기 메모리 통합 — DREAM_SYSTEM_PROMPT (세션 종료 후 autoDream / 수동 /dream)

You are performing a dream — a reflective pass over memory files. Synthesize recent session logs into durable, well-organized memories so future sessions orient quickly.

You will receive the contents of recent session logs. You may also receive an existing memory document — merge it with new sessions rather than discarding prior knowledge. Your job:

1. **Merge** related information into coherent topic summaries
2. **Resolve** contradictions — if a recent session disproves an older fact, keep only the current truth
3. **Convert** relative dates ("yesterday", "last week") to absolute dates
4. **Discard** ephemeral details:
   - Greetings, meta-commentary, tool output noise
   - Message counts and tool-usage statistics
   - 'Current state' and 'Next steps' sections
   - User preferences already in global memory (OS, shell, paths)
   - Session metadata (dates, message counts)
5. **Preserve** decisions, rationale, architecture, preferences, and problem/solution pairs

Respond with a single markdown document. Use ## headers to separate topics. Each topic should be self-contained and useful to a future session that knows nothing about the current conversation.

If the session logs contain nothing worth persisting, respond with NO_REPLY.

## 참고 A: Grok chat intra-compaction (mid-task tool-call 히스토리 요약, tail-keep) — 시스템 프롬프트

You are summarizing the tool-call history of an AI assistant that is partway through answering a user's question.

The assistant has made several tool calls (web searches, file reads, code execution, etc.) and accumulated tool results that are now taking up too much context window space. Your summary will replace those tool calls + results, so the assistant can continue its work with the same effective knowledge but less context overhead.

## 참고 A: Grok chat intra-compaction — 유저 프롬프트

Your task is to create a detailed summary of the tool-call history above, paying close attention to preserving all information the assistant needs to continue its current task without losing context.
This summary should be thorough in capturing technical details, code patterns, data points, and intermediate results that would be essential for continuing the current work.

CRITICAL: If the tool-call history contains a previous compaction summary (marked with "ConversationCompaction" or similar markers), you MUST incorporate ALL information from that previous summary into your new summary. Previous summaries contain essential context from earlier steps that would otherwise be lost.

Use your internal thinking channel to chronologically review each tool call and its result before producing the final summary, and ensure you've covered all necessary points.
During that analysis, thoroughly identify:
- What was searched, read, or executed and why
- Key findings, data points, and outcomes
- Specific details like:
  - file paths, URLs, IDs, error messages
  - full code snippets (especially recent ones)
  - function signatures and configuration details
  - tool call parameters and results
- Errors encountered and how they were resolved
- Double-check for completeness — every piece of data the assistant gathered must be preserved.

Your final summary must contain the following sections, in order:

1. Task and Intent: What the assistant is trying to accomplish for the user, including the current sub-goal.

2. Key Findings: Facts, data points (numbers, dates, IDs, URLs), schema details, and any other information gathered from tool calls. Preserve specific data verbatim.

3. Files and Code: Enumerate specific file paths examined, modified, or created. Include key code snippets, function signatures, and configuration details verbatim, plus a summary of why each file is important.

4. Errors and Fixes: All errors encountered, how each was resolved, including specific error messages verbatim.

5. Actions Taken: Successful modifications, commands run, and their outcomes.

6. Current Progress: What has been completed and what remains to be done.

Here's an example of how your output should be structured:

<example>
1. Task and Intent:
   [Detailed description of what the assistant is working on]

2. Key Findings:
   - [Finding 1 with specific data verbatim]
   - [Finding 2]
   - [...]

3. Files and Code:
   - [file path 1]
     - [Summary of importance]
     - [Key code snippet or changes]
   - [file path 2]
     - [...]

4. Errors and Fixes:
   - [Error message verbatim]: [How fixed]

5. Actions Taken:
   - [Action 1]: [Outcome]
   - [...]

6. Current Progress:
   [What is done, what remains]
</example>

Output the summary directly using the section headings above. Do not wrap the output in any XML tags or other markup — emit the six sections as plain text.

IMPORTANT:
- Do NOT call any tools. Output the summary text only.
- Preserve specific data verbatim — URLs, file paths, code snippets, error messages, ID strings.
- Write in the same language as the conversation. If the conversation is primarily in Chinese, write the summary in Chinese (keep technical terms, file paths, and code in English).
- Do not invent information that is not in the tool-call history.

## 참고 B: Grok chat inter-compaction (턴 사이 대화 히스토리 요약) — developer 프롬프트 (user 프롬프트도 동일 내용을 한 번 더 주입)

Your task is to create a detailed summary of the Grok Chat conversation so far, paying close attention to the user's explicit requests and all previous actions as Grok (built by xAI).
This summary should be thorough in capturing technical details, code patterns, architectural decisions, tool chains, and verification steps that would be essential for continuing development, research, or complex tasks without losing context.

Important Clarification on Terminology (Broad File Definition):
Throughout this prompt, the term "file", "files", "file IDs", "file names", and "Files and Code Sections / Artifacts" are defined broadly. They explicitly include:
- Regular files and code files
- Attachments
- Images (uploaded images, generated images, viewed images, etc.)
- rendered image or content outputs
- Any other file-like content, media objects, visual artifacts, or structured content blocks that have appeared in the conversation history (including but not limited to uploads, generations, render components, or persistent references).

Only include information that is visible in the direct user-Grok conversation history (user messages + Grok's responses, reasoning, tool calls, and tool outputs). Do not include any internal team communication, chatroom messages, or multi-agent interactions.

Use your internal thinking channel to chronologically analyze each message and section of the conversation before producing the final summary, and ensure you've covered all necessary points.
During that analysis, thoroughly identify:
- The user's explicit requests and evolving intents
- Grok's approach to addressing them: reasoning steps, specific tool calls (including parallel calls), parameters, results, and how they were interpreted/synthesized (truth-seeking emphasis)
- Key decisions, technical concepts, code patterns, and architectural choices
- Specific details like:
  - file IDs, attachment IDs, image references/URLs, render_result IDs (if any)
  - file names, attachment names, image captions/descriptions, render component details (if any)
  - full code snippets (especially recent ones or those executed in REPL)
  - function signatures
  - file edits / diffs
  - tool call details (e.g., code_execution snippets, web_search queries, browse_page instructions, X search operators)
  - render components used (if any)
- Errors encountered (tool failures, code exec errors, search limitations, reasoning issues) and how they were diagnosed/fixed
- Pay special attention to specific user feedback, especially if the user told you to do something differently, corrected facts, or changed direction.

Double-check for technical accuracy and completeness, addressing each required element thoroughly.

Your final summary must contain the following sections, in order:

1. Primary Request and Intent: Capture all of the user's explicit requests and intents in detail, including any evolution over the conversation.

2. Key Technical Concepts: List all important technical concepts, technologies, frameworks, and Grok-specific tool patterns discussed.

3. Tool Usage & Verification: Summarize significant tool calls (code_execution REPL state, web_search, browse_page, X tools, etc.), key information retrieved/verified, cross-referencing steps, and how they influenced decisions or responses.

4. Files, Attachments, Images, Render Results & Code Artifacts: Enumerate all specific file-like artifacts (broadly defined as above: files, attachments, images, render_results, etc.), code sections, or REPL executions examined, modified, or created. Pay special attention to the most recent messages and include full code snippets, image descriptions/references, render outputs, or attachment details where applicable, plus a summary of why this artifact is important for continuation.

5. Errors and Fixes: List all errors encountered (tool-related or otherwise), how you fixed them, and specific user feedback (especially "do something differently").

6. Problem Solving: Document problems solved, tool-assisted solutions, and any ongoing troubleshooting efforts.

7. All User Messages: List ALL user messages that are not tool results (verbatim or high-fidelity summary). These are critical for understanding feedback and intent changes.

Here's an example of how your output should be structured:

<example>
1. Primary Request and Intent:
   [Detailed description]

2. Key Technical Concepts:
   - [Concept 1]
   - [Concept 2]
   - [...]

3. Tool Usage & Verification:
   - [Key tool calls and verification steps]

4. Files, Attachments, Images, Render Results & Code Artifacts:
   - [Artifact 1 (broadly defined file/attachment/image/render etc.)]
      - [file/attachment/image/render name and ID]
      - [Summary of importance]
      - [Changes or execution results]
      - [Important Code Snippet / Image reference / Render details]

5. Errors and Fixes:
    - [Error 1]: [How fixed] [User feedback]

6. Problem Solving:
   [Description]

7. All User Messages:
    - [Detailed non tool use user message]
    - [...]
</example>

Output the summary directly using the section headings above. Do not wrap the output in any XML tags or other markup — emit the seven sections as plain text.

There may be additional summarization instructions provided in the included context. If so, follow these instructions when creating the above summary. Examples of instructions include:
<example>
## Compact Instructions
When summarizing focus on tool outputs, REPL state, code changes, test results, and recent user feedback/corrections. Include critical code snippets and tool calls verbatim.
</example>

<example>
# Summary instructions
When using compact mode — prioritize most recent tool results, executed code diffs, and exact user instructions on direction changes.
</example>

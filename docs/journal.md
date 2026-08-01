# DashTrack — Development Journal

## Session 1 — Phase 0: Foundations & Planning
**Date:** 2026-07-28

### Problem being solved this session
Define *what DashTrack is and isn't* before writing any code. Produce the Phase 0 planning artifacts: problem statement, persona, data model, user stories, MVP scope, non-goals, risks, decision log, and system architecture.

### What DashTrack is
**Problem statement:** A gig delivery driver wants to know whether their shifts are actually worth the time and money they cost. Platforms like DoorDash show per-delivery payouts but not the true cost of a shift — total time spent driving/waiting/finding addresses, total miles, or vehicle cost. Existing driver apps focus heavily on tax-deduction mileage logging and put better features behind subscriptions. In their absence, a driver like me records shifts by hand (odometer photos, notebooks, phone notes) that are hard to organize or analyze — so it's difficult to tell which shifts, days, or hours are genuinely profitable.

**Project motivation (kept separate from problem, for honesty):** A learning project to understand full-stack development end to end and build the specific metrics I care about without a subscription. Not intended to compete commercially.

**Persona:** Part-time DoorDash driver (myself), electric car, phone-first, values low-friction logging, accesses the app via phone web browser at a URL (not a native app).

### Data model (settled)
- **Shift** ("session"): a container belonging to one user; has start, end, rolled-up totals. Only one active shift at a time.
- **Delivery**: many per shift. Captures start-time + end-time (auto, via tapping start/stop), miles (typed, required), earnings (typed, optional — fillable later), battery used (typed), optional zone (dropdown). Only one active delivery at a time.
- One-to-many: one shift has many deliveries; shift rolls them up.

### Key decisions made (with reasoning)
1. **Shift contains individual deliveries (one-to-many), live-logged.** Chosen over shift-totals-only because per-delivery detail is the whole motivation. Tradeoff: more build complexity + in-shift friction; mitigated by building incrementally from a simpler core.
2. **Web app, not native.** Deploys once, runs on any phone, plays to learning goals; PWA can recover convenience later. Tradeoff: slightly more launch friction; no deep native features (this bites us on the timer — see risks).
3. **Per-delivery mileage = one typed number** (not two, not OCR). The two-number split and OCR both failed the "would I act on this?" test / were too costly. Parked to v2.
4. **Zone captured via hardcoded dropdown (~5–6 SD zones), optional; per-zone metrics deferred to v2.** Free-text rejected (dirty data breaks grouping); user-managed list rejected (unjustified scope). Metrics need weeks of data, so they're a poor fit for a value-immediately MVP.
5. **Two levels of metrics:** per-delivery computed on delivery-end; per-shift computed on shift-end.

### Alternatives considered & rejected (v2 backlog)
Odometer OCR/photo auto-fill; two-number mileage split; per-zone profitability metrics; GPS-based zones; user-managed zone lists; native app / PWA install. All parked *with reasons*, not deleted.

### Risk register (found this session)
1. Abandoned (never-ended) shift/delivery → corrupt metrics. *[High × Med]*
2. **Browser backgrounds/kills the tab → live timer lost.** *[High × High — the central challenge]* Fix shape: store start/end timestamps, don't run a ticking clock; duration = end − start, which survives the tab freezing.
3. Multi-device login → conflicting active session. *[Med × Low]* — edge case for single-user app.
4. **Floating-point money errors → wrong totals.** *[High × Med]* Store money as an exact type (integer cents / decimal), never float.
5. Overnight shift crosses midnight → wrong hours / day-grouping. *[Med × Med]*

### Concepts learned - **Store timestamps, don't run clocks:** duration derived from two fixed instants is robust to the browser freezing the tab, because nothing needs to happen *between* the two readings — the system clock keeps time regardless.
- **Authentication vs authorization:** authn = *who are you* (login/credentials); authz = *what you're allowed to do* — split into **action** authorization (can you do this kind of thing) and **ownership** authorization (is *this specific record* yours). DashTrack barely needs action-authz (no roles) but must enforce **ownership** on every request touching a specific shift/delivery.
- **IDOR (Insecure Direct Object Reference):** the bug where the backend authenticates but forgets to authorize ownership, letting a logged-in user reach another user's records by changing an ID. Rule: never trust a user-supplied ID without verifying ownership server-side.
- **System architecture as trust/responsibility map:** browser shows & captures (untrusted) → Next.js presents & translates → FastAPI decides/calculates/authorizes (the *only trusted box*) → PostgreSQL remembers & protects. Every arrow crosses a boundary. Chose separate FastAPI backend over Next.js-does-everything because seeing the client-server boundary teaches more.

### Lessons learned
- Most of "engineering" so far has been **saying no to features.** Killed three (OCR, two-number mileage, zone metrics) using one reusable test: *"would this produce something I'd actually act on? If my behavior wouldn't change, it doesn't belong in the MVP."* (Caveat: this test is for analytics/convenience features, not security/backup/legal ones.)
- Requirements → design → code, cheapest to most expensive to change. Doing the thinking in English first is why none of these decisions cost real time to make or revise.

### Status
Phase 0 essentially complete. One item (define the first concrete Phase-1 milestone) deferred to next session as the on-ramp to environment setup.

DashTrack — Decision Log

# DashTrack — Decision Log

Architectural and tooling decisions, each with the context, the options weighed, the
choice, the reasoning, and the tradeoffs accepted. Newest at the bottom.

> Note: Phase 0 product decisions (web-app-not-native, shift-contains-deliveries data
> model, per-delivery manual mileage, zone metrics deferred to v2) were logged in the
> Phase 0 planning session and should be transferred here from those notes.

---

## D-01 — Monorepo (single repository)

- **Context:** Solo developer, one product; frontend and backend share an API contract
  that changes together.
- **Options considered:** Monorepo (backend/ + frontend/ as siblings) vs. polyrepo
  (two separate repositories).
- **Chosen:** Monorepo.
- **Reason:** Atomic commits keep the API contract in sync across both sides — a single
  commit can update the endpoint and its caller, so history never drifts. One clone,
  one CI pipeline, less overhead for a solo dev.
- **Tradeoffs:** Polyrepo is better at team scale — separate ownership, independent
  deploy cadences, per-repo access control. Would reconsider at that scale.
- **Date:** 2026-07-30

---

## D-02 — WSL2 over native Windows for development

- **Context:** Developing on a Windows machine, deploying to a Linux server; Docker
  Desktop already runs on the WSL2 backend.
- **Options considered:** Native Windows (PowerShell, Windows Python/Node, project on
  `C:\`) vs. WSL2 (Ubuntu, Linux toolchain and filesystem).
- **Chosen:** WSL2 with Ubuntu 24.04 LTS.
- **Reason:** Dev environment matches the Linux production target; Docker integrates
  cleanly; avoids Windows/Linux line-ending (CRLF/LF) friction. Learning curve is real
  but front-loaded and small given a Computer Engineering / Linux background.
- **Tradeoffs:** Adds a second filesystem and some setup friction up front vs. starting
  faster on native Windows.
- **Date:** 2026-07-30

---

## D-03 — Project lives in the Linux home (`~/`), not `/mnt/c`

- **Context:** WSL2 mounts the Windows `C:` drive at `/mnt/c`. Files there cross the
  Windows(NTFS)↔Linux(ext4) boundary on every operation.
- **Options considered:** Develop on `/mnt/c` (the Windows drive) vs. `~` (native Linux
  filesystem).
- **Chosen:** `~/dashtrack` (native Linux filesystem).
- **Reason:** No boundary crossing → fast file operations (critical for Git and
  `npm install`, which touch many small files) and correct Linux permissions; tools
  behave as they will in production.
- **Tradeoffs:** Files aren't in the default Windows Explorer view — reachable via
  `\\wsl$` and VS Code, so not a real loss.
- **Date:** 2026-07-30

---

## D-04 — Use uv (not bare pip + venv) for Python dependency management

- **Context:** New solo project; goals include reproducibility and learning the
  fundamentals.
- **Options considered:** `pip` + `venv` (+ `requirements.txt`) — the universal
  baseline — vs. `uv` (unified, fast, lockfile-based).
- **Chosen:** uv.
- **Reason:** Lockfile reproducibility (`uv.lock`), a unified toolchain (versions +
  isolation + install + lock in one tool), and it's the de-facto standard for new
  Python projects in 2026. The manual venv model was learned first, so uv automates a
  concept already understood rather than hiding it.
- **Tradeoffs:** `pip` + `venv` is the lingua franca some interviewers assume; uv
  automates activation, so must retain understanding of the underlying venv model.
- **Date:** 2026-07-30

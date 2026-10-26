# 0005 — Viewer in the browser with Three.js

**Status:** Accepted (2026-10-25). Supersedes the earlier Godot plan.

**Context.** The replay should be viewable by anyone with a link, deployable to the existing VPS, and testable with the owner's existing Playwright/TypeScript skills. The future world builder should share the renderer.

**Decision.** Vite + TypeScript + Three.js, plain DOM UI, an orthographic camera at the isometric angle over a real 3D scene (not 2D iso tiles), fully bundled with no runtime CDN.

**Consequences.** No editor or built-in particle system as in Godot; effects are hand-made (fine at this scale). Easy e2e and screenshot testing with Playwright. Strict CSP is possible.

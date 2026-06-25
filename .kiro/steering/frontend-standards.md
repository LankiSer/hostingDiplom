---
inclusion: fileMatch
fileMatchPattern: ['frontend/**/*.{ts,vue}']
---

# Frontend Standards

- Use TypeScript everywhere, including `script setup lang="ts"` in Vue files.
- Follow `common` for API domains and `shared` for project-level reusable modules.
- Keep files short; split files larger than 100 lines into `component`, `interface`, `hooks`, `providers`, or `.partials`.
- Put props and public interfaces into nearby `interface.ts` files.
- Build internal UI primitives in `shared/app/components` instead of relying on a heavy UI framework.
- Keep pages thin and move display logic into domain or shared components.

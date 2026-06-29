# VeltaCapital — site prototype

A three-page front-end for the VeltaCapital chart-reading platform, built to run
on GitHub Pages. The **design, copy, page flow, and the game are real.** Login,
payment, and plan-gating are **simulated** — clearly marked stubs to be replaced
by a real backend later.

## Pages

- **index.html** — Landing page. Hero, how-it-works, course + bios, embedded
  3-round trial of the game, pricing, contact. The trial gives 3 rounds, then
  prompts a (simulated) Google login.
- **member.html** — The signed-in area. Two states in one page:
  - *Before purchase:* a conversion page showing the credits earned in the
    trial and what a plan unlocks, with a payment pop-up.
  - *After purchase:* a 3-tab member area — Course videos, Prediction game,
    Redeem credits — gated by the chosen plan.
- **predict-the-graph.html** — The game itself (also embedded in the two pages).

## What's real vs. simulated

Real: every page, all visual design, all marketing copy, the working game,
the credit math, the reward ladder, plan definitions, the whole click-through
flow.

Simulated (look in `assets/velta.js`, every stub is marked `// [BACKEND]`):
- **Login** — "Continue with Google" just flips a local flag. No real auth.
- **Payment** — "Choose plan" sets a local plan. No real money, no Stripe.
- **Plan/credits** — stored in the browser only; a user could edit them.

These three are exactly the things that need a server, which GitHub Pages
can't provide. The prototype lets you design and demo the entire experience
now; the backend gets wired in when you move to a host that supports it
(and when the payment/legal operator is sorted).

### Previewing the plans
On `member.html`, the top-right badge shows the current simulated plan. Use the
tier buttons to "buy" a plan and preview that tier's member area. "Reset preview"
(top nav) clears the simulated state and returns to the landing page.

## To edit before launch

Search the files for `[PLACEHOLDER]`:
- Your bio and Saechan's bio (index.html, "The course" section)
- Instagram / email / phone (index.html contact + footer)
- Prices and plan details (assets/velta.js → `PLANS`)
- Video titles (filled when Saechan's videos are ready)

## Deploying on GitHub Pages

Put all files (keep the `assets/` folder) at the repo root, then
**Settings → Pages → Deploy from a branch → main / root.**
Site appears at `https://<username>.github.io/<repo>/`.

## Data for the game

Same as before: run `build_rounds.py` on your own computer to generate
`rounds.json` (real chart data), then commit it. Without it, the game runs on
built-in practice charts.

## Important

Login/payment here are not secure and must not be used to take real money.
This is a design prototype. The educational disclaimers in the footer should
stay in the real product.

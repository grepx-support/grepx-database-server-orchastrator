# grepx-split - LifeFlow Blood Camp deployment

On the server (Linux, git, an SSH key GitHub accepts), one command installs or updates everything:

```bash
curl -fsSL https://raw.githubusercontent.com/grepx-support/grepx-database-server-orchastrator/blood-donation/install.sh | bash
```

First time, add your site address and admin in front of `bash`:

```bash
curl -fsSL https://raw.githubusercontent.com/grepx-support/grepx-database-server-orchastrator/blood-donation/install.sh \
  | SITE_URL=https://your.site ADMIN_EMAIL=you@example.com ADMIN_PASSWORD='…' ADMIN_PHONE='9123 4567' bash
```

It clones this repo into ~/grepx-database-server-orchastrator, the four app repos next to the orchestrator, builds Nexus,
sets everything up, generates the secrets in .env, migrates, starts and seeds. The app is then in
~/grepx-database-server-orchastrator/grepx-blood-donation (`scripts/run.sh status | logs | restart`).

| Repo (cloned next to each other) | What |
|---|---|
| grepx-blood-donation | the product and the workspace (`deploy.sh`, `workspace.sh`) |
| grepx-platform | libraries, tools, scripts, monitoring |
| grepx-services | generic services |
| grepx-nexus-cpp | the Nexus server (built with cmake) |

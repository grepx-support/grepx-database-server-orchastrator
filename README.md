# grepx-split - LifeFlow Blood Camp deployment

On the server (Linux, git, an SSH key GitHub accepts):

```bash
git clone git@github.com:grepx-support/grepx-database-server-orchastrator.git
cd grepx-database-server-orchastrator
git checkout blood-donation
./install.sh
```

First time only, create your admin and set your site address:

```bash
cd grepx-blood-donation
scripts/run.sh admin you@example.com YourPassword "Your Name" "9123 4567"
nano .env        # SITE_URL=https://your.site, then: scripts/run.sh restart
```

Update later: `./install.sh` again (in grepx-database-server-orchastrator).
Secrets in .env are generated automatically the first time.

| Repo (cloned next to each other) | What |
|---|---|
| grepx-blood-donation | the product and the workspace (`deploy.sh`, `workspace.sh`) |
| grepx-platform | libraries, tools, scripts, monitoring |
| grepx-services | generic services |
| grepx-nexus-cpp | the Nexus server (built with cmake) |

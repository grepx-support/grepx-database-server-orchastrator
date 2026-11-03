# grepx-split - LifeFlow Blood Camp deployment

One command gets, builds and runs everything (Linux / WSL):

```bash
git clone -b blood-donation https://github.com/grepx-support/grepx-database-server-orchastrator.git grepx-split
cd grepx-split/orchestrator
./setup.sh                              # once
./run.sh -p grepx-blood-donation        # clone/update the 4 repos, build Nexus, set up, migrate, start, seed
```

Update later: run the same `./run.sh -p grepx-blood-donation` again (pulls, rebuilds, restarts).
`--fetch-only` only clones/updates. First time: `cd ../grepx-blood-donation && scripts/run.sh admin EMAIL PASS "NAME" PHONE`.

| Repo (cloned next to each other) | What |
|---|---|
| grepx-blood-donation | the product and the workspace (`deploy.sh`, `workspace.sh`) |
| grepx-platform | libraries, tools, scripts, monitoring |
| grepx-services | generic services |
| grepx-nexus-cpp | the Nexus server (built with cmake) |

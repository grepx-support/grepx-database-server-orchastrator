# GrepX orchestrator

One orchestrator installs any number of GrepX projects on a server. Each project is described by one file in
`orchestrator/projects/<name>.yaml` and is installed into its own folder here, with its own repos and its own Nexus.

```bash
git clone https://github.com/grepx-support/grepx-database-server-orchastrator.git
cd grepx-database-server-orchastrator
git checkout blood-donation
./install.sh -h                 # help + the list of projects
./install.sh blood-donation     # install / update LifeFlow Blood Camp  -> ./blood-donation/
```

Update later: `./install.sh blood-donation` again. First time only: create the admin in
`blood-donation/grepx-blood-donation` with `scripts/run.sh admin EMAIL PASSWORD "NAME" PHONE`.

```
grepx-database-server-orchastrator/
├── install.sh                       the only command
├── orchestrator/
│   ├── orchestrator.py, setup.sh, requirements.txt
│   └── projects/
│       ├── blood-donation.yaml      skip: false
│       └── kitchen.yaml             skip: true (template)
├── blood-donation/                  created by ./install.sh blood-donation
│   ├── grepx-blood-donation/        the app - run scripts/run.sh … here
│   ├── grepx-platform/  grepx-services/  grepx-nexus-cpp/
└── logs/                            orchestrator logs, one per project per day
```

Add a project: copy `orchestrator/projects/blood-donation.yaml` to `<name>.yaml`, change `description`, `folder`,
`repo` and `skip: false`. Two projects on one server need different ports (their own `config/services.ini` and Nexus
port in `config/common.yaml`).

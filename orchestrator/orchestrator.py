# orchestrator/orchestrator.py
#!/usr/bin/env python3
"""One orchestrator, many projects. Each project is described by its own file in projects/<name>.yaml and is installed
into its own folder next to this orchestrator (<root>/<folder>/), with its own repos - its own Nexus included.

    ./run.sh -l                 list the projects (and whether each is skipped or installed)
    ./run.sh -p blood-donation  clone/update that project's repos into <root>/blood-donation/ and run its deploy
    ./run.sh -a                 every project that is not `skip: true`
    --fetch-only                clone/update only, no deploy step

projects/<name>.yaml
    description: LifeFlow Blood Camp
    skip: false                         # true = never installed (also not by -a); -p refuses it
    folder: blood-donation              # optional, default: the file name
    repo: {name: grepx-blood-donation, url: …, branch: main}        # the project repo: where deploy runs
    deploy: bash deploy.sh --no-pull    # optional, run inside the project repo after fetching
    env: {KEY: value}                   # optional, extra environment for the deploy
    dependencies:                       # other repos, cloned into the same folder
      grepx-platform: {url: …, branch: main}            # -> <folder>/grepx-platform
      some-lib: {url: …, branch: main, path: libs/x}    # -> <folder>/libs/x
"""
import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
PROJECTS_DIR = SCRIPT_DIR / "projects"
LOG_DIR = ROOT_DIR / "logs"


def setup_logging(project=None):
    LOG_DIR.mkdir(exist_ok=True)
    name = f"orchestrator_{project + '_' if project else ''}{datetime.now().strftime('%Y%m%d')}.log"
    # Same line format as install.sh, setup.sh and the platform scripts: 2026-11-07 18:30:00 INFO  [orchestrator] message
    logging.addLevelName(logging.WARNING, "WARN")
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-5s [orchestrator] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler(LOG_DIR / name), logging.StreamHandler(sys.stdout)])
    return logging.getLogger(__name__)


def load_projects():
    """{name: config} from projects/*.yaml, the name being the file name."""
    projects = {}
    for path in sorted(PROJECTS_DIR.glob("*.yaml")):
        config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        config.setdefault("folder", path.stem)
        projects[path.stem] = config
    return projects


def is_skipped(config):
    return str(config.get("skip", False)).lower() in ("true", "yes", "1")


def run_cmd(cmd, cwd=None, env=None):
    return subprocess.run(cmd, shell=True, cwd=cwd, env=env).returncode == 0


def clone_or_update(name, url, branch, target_dir, logger):
    if (target_dir / ".git").exists():
        logger.info(f"Updating {name} ({branch})")
        ok = run_cmd(f"git fetch -q origin {branch} && git checkout -q {branch} && git pull -q --ff-only origin {branch}",
                     cwd=target_dir)
    else:
        logger.info(f"Cloning {name} ({branch}) from {url}")
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        ok = run_cmd(f"git clone -q -b {branch} {url} {target_dir}")
    (logger.info if ok else logger.error)(f"{name}: {'ready' if ok else 'could not be fetched'}")
    return ok


def project_dir(config):
    return ROOT_DIR / config["folder"]


def fetch_project(name, config, logger):
    base = project_dir(config)
    repo = config["repo"]
    ok = clone_or_update(repo["name"], repo["url"], repo.get("branch", "main"), base / repo["name"], logger)
    for dep_name, dep in (config.get("dependencies") or {}).items():
        ok = clone_or_update(dep_name, dep["url"], dep.get("branch", "main"), base / dep.get("path", dep_name), logger) and ok
    return ok


def run_deploy(name, config, logger):
    command = config.get("deploy")
    if not command:
        return True
    repo_path = project_dir(config) / config["repo"]["name"]
    logger.info(f"Deploying {name}: {command}")
    env = {**os.environ, **{k: str(v) for k, v in (config.get("env") or {}).items()}}
    ok = run_cmd(command, cwd=repo_path, env=env)
    (logger.info if ok else logger.error)(f"Deploy {'finished' if ok else 'FAILED'}: {name}")
    return ok


def install(name, config, logger, fetch_only=False):
    logger.info("=" * 50)
    logger.info(f"{name}: {config.get('description', '')} -> {project_dir(config)}")
    logger.info("=" * 50)
    if not fetch_project(name, config, logger):
        logger.error(f"{name}: some repositories could not be fetched")
        return False
    return True if fetch_only else run_deploy(name, config, logger)


def list_projects(projects):
    print("Projects (orchestrator/projects/*.yaml):")
    for name, config in projects.items():
        state = "skip" if is_skipped(config) else ("installed" if project_dir(config).exists() else "not installed")
        deps = len(config.get("dependencies") or {})
        print(f"  {name:<20} {state:<14} {config.get('description', '')}  [{deps} repos + {config['repo']['name']} -> {config['folder']}/]")


def main():
    parser = argparse.ArgumentParser(description="Install / update GrepX projects (one folder per project).")
    parser.add_argument("-p", "--project", help="project to install (a file name in projects/)")
    parser.add_argument("-l", "--list", action="store_true", help="list the projects")
    parser.add_argument("-a", "--all", action="store_true", help="install every project that is not skip: true")
    parser.add_argument("--fetch-only", action="store_true", help="clone/update the repos only, no deploy step")
    args = parser.parse_args()

    projects = load_projects()
    if not projects:
        print(f"No projects in {PROJECTS_DIR}")
        return 1
    if args.list or not (args.project or args.all):
        list_projects(projects)
        return 0
    if args.all:
        logger = setup_logging()
        wanted = {n: c for n, c in projects.items() if not is_skipped(c)}
        for n in set(projects) - set(wanted):
            logger.info(f"{n}: skipped (skip: true)")
        results = [install(n, c, logger, args.fetch_only) for n, c in wanted.items()]
        return 0 if all(results) else 1
    if args.project not in projects:
        print(f"Unknown project '{args.project}'. Available: {', '.join(projects)}")
        return 1
    if is_skipped(projects[args.project]):
        print(f"Project '{args.project}' is marked skip: true in projects/{args.project}.yaml - set it to false to install it")
        return 1
    logger = setup_logging(args.project)
    return 0 if install(args.project, projects[args.project], logger, args.fetch_only) else 1


if __name__ == "__main__":
    sys.exit(main())

# orchestrator/orchestrator.py

# !/usr/bin/env python3
import os
import sys
import subprocess
import yaml
import argparse
import logging
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SCRIPT_DIR / "orchestrator.yaml"
LIBS_DIR = ROOT_DIR / "libs"
LOG_DIR = ROOT_DIR / "logs"


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_DIR / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0


def clone_or_update(name, url, branch, target_dir, logger):
    if target_dir.exists():
        logger.info(f"Updating {name} from {branch}...")
        success = run_cmd(f"git pull origin {branch}", cwd=target_dir)
        if success:
            logger.info(f"{name} updated")
        return success
    else:
        logger.info(f"Cloning {name} from {url}...")
        success = run_cmd(f"git clone -b {branch} {url} {target_dir}")
        if success:
            logger.info(f"{name} cloned")
        return success


def fetch_dependency(dep_name, dep_config, logger):
    url = dep_config['url']
    branch = dep_config.get('branch', 'main')

    # `dir:` places the repo relative to the orchestrator root (e.g. next to the project that links it in);
    # without it, dependencies go to libs/<path> as before.
    dep_path = ROOT_DIR / dep_config['dir'] if 'dir' in dep_config else LIBS_DIR / dep_config['path']
    dep_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Fetching dependency: {dep_name}")
    return clone_or_update(dep_name, url, branch, dep_path, logger)


def fetch_server(server_name, server_config, project_dir, logger):
    url = server_config['url']
    branch = server_config.get('branch', 'main')
    path = server_config['path']

    # Servers go inside the project directory
    server_path = project_dir / path
    server_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Fetching server: {server_name}")
    return clone_or_update(server_name, url, branch, server_path, logger)


def fetch_all_dependencies(config, logger):
    logger.info("=" * 50)
    logger.info("Fetching all dependencies")
    logger.info("=" * 50)

    all_deps = config.get('dependencies', {})
    if not all_deps:
        logger.info("No dependencies to fetch")
        return True

    for dep_name, dep_config in all_deps.items():
        fetch_dependency(dep_name, dep_config, logger)

    logger.info("All dependencies fetched")
    return True


def run_deploy(project_name, project_config, project_path, logger):
    """Optional `deploy:` command, run inside the project after everything is fetched (with optional `env:`)."""
    command = project_config.get('deploy')
    if not command:
        logger.info(f"Run 'cd {project_name} && ./setup.sh' to install dependencies")
        return True
    logger.info(f"Step 4: Deploying ({command})")
    env = {**os.environ, **{k: str(v) for k, v in (project_config.get('env') or {}).items()}}
    ok = subprocess.run(command, shell=True, cwd=project_path, env=env).returncode == 0
    (logger.info if ok else logger.error)(f"Deploy {'finished' if ok else 'FAILED'}: {project_name}")
    return ok


def deploy_project(project_name, config, logger, fetch_only=False):
    if project_name not in config.get('projects', {}):
        logger.error(f"Project '{project_name}' not found in config")
        return False

    logger.info("=" * 50)
    logger.info(f"Starting deployment: {project_name}")
    logger.info("=" * 50)

    project_config = config['projects'][project_name]
    url = project_config['url']
    branch = project_config.get('branch', 'main')
    deps = project_config.get('dependencies', [])
    servers = project_config.get('servers', [])

    project_path = ROOT_DIR / project_name

    logger.info(f"Step 1: Cloning/updating project repository")
    if not clone_or_update(project_name, url, branch, project_path, logger):
        return False

    if deps:
        logger.info(f"Step 2: Fetching {len(deps)} dependencies")
        all_deps = config.get('dependencies', {})
        for i, dep in enumerate(deps, 1):
            if dep in all_deps:
                logger.info(f"[{i}/{len(deps)}] Fetching {dep}")
                fetch_dependency(dep, all_deps[dep], logger)

    if servers:
        logger.info(f"Step 3: Fetching {len(servers)} servers")
        all_servers = config.get('servers', {})
        for i, server in enumerate(servers, 1):
            if server in all_servers:
                logger.info(f"[{i}/{len(servers)}] Fetching {server}")
                fetch_server(server, all_servers[server], project_path, logger)

    ok = True if fetch_only else run_deploy(project_name, project_config, project_path, logger)
    logger.info("=" * 50)
    logger.info(f"Deployment {'completed' if ok else 'failed'}: {project_name}")
    logger.info("=" * 50)
    return ok


def list_projects(config):
    print("\nConfigured Projects:")
    for name, proj in config.get('projects', {}).items():
        branch = proj.get('branch', 'main')
        deps_count = len(proj.get('dependencies', []))
        servers_count = len(proj.get('servers', []))
        status = "Deployed" if (ROOT_DIR / name).exists() else "Not Deployed"
        print(f"  - {name} (branch: {branch})")
        print(f"    Dependencies: {deps_count}, Servers: {servers_count} [{status}]")


def main():
    parser = argparse.ArgumentParser(description='Orchestrator')
    parser.add_argument('-p', '--project', help='Project name to deploy')
    parser.add_argument('-l', '--list', action='store_true', help='List all projects')
    parser.add_argument('-a', '--all', action='store_true', help='Deploy all projects')
    parser.add_argument('--fetch-deps', action='store_true', help='Fetch all dependencies')
    parser.add_argument('--fetch-only', action='store_true', help='Clone/update repos but skip each project\'s deploy: step')

    args = parser.parse_args()

    if not CONFIG_FILE.exists():
        print(f"Error: Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)

    logger = setup_logging()

    if args.list:
        list_projects(config)
    elif args.fetch_deps:
        fetch_all_dependencies(config, logger)
    elif args.all:
        results = [deploy_project(name, config, logger, args.fetch_only) for name in config.get('projects', {})]
        sys.exit(0 if all(results) else 1)
    elif args.project:
        sys.exit(0 if deploy_project(args.project, config, logger, args.fetch_only) else 1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3

import os
import subprocess
import sys
from time import sleep
import apt_pkg
import git.config
from github import Github
from launchpadlib.launchpad import Launchpad
import git

DEFAULT_SERIES_NAME = "noble"

def get_packages_list() -> list:
    with open("/tmp/patched-packages", 'r', encoding='utf-8') as file:
        items = file.read().splitlines()
    return items

def github_pull_exists(title, repo):
    """Check if GitHub Actions has already opened a PR with this title"""
    open_pulls = repo.get_pulls(state="open")
    for open_pull in open_pulls:
        if open_pull.title == title and open_pull.user.login == "github-actions[bot]":
            return True
    return False

def get_upstream_sources():
    """Get the current version of a package in upstream PPA"""
    return ubuntu_archive.getPublishedSources(
        exact_match=True,
        source_name=component_name,
        status="Published",
        pocket=pocket,
        distro_series=upstream_series,
    )

def main():
    series_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SERIES_NAME

    # Configuring this repo to be able to commit as a bot
    current_repo = git.Repo('.')
    with current_repo.config_writer() as git_config:
        git_config.set_value('user', 'email', "github-actions[bot]@users.noreply.github.com")
        git_config.set_value('user', 'name', "github-actions[bot]")
        git_config.add_value('safe','directory', "/__w/os-patches/os-patches")


    current_repo.git.fetch("--all")

    # github_token = os.environ["GITHUB_TOKEN"]
    # github_repo = os.environ["GITHUB_REPOSITORY"]
    # github = Github(github_token)
    # repo = github.get_repo(github_repo)



    # Initialize APT
    apt_pkg.init_system()

    # Initialize Launchpad variables
    launchpad = Launchpad.login_anonymously(
        "elementary daily test", "production", "~/.launchpadlib/cache/", version="devel"
    )

    ubuntu = launchpad.distributions["ubuntu"]
    ubuntu_archive = ubuntu.main_archive
    patches_archive = launchpad.people["elementary-os"].getPPAByName(
        distribution=ubuntu, name="os-patches"
    )

    packages_and_upstream = get_packages_list()

    for package_and_upstream in packages_and_upstream:
        package_name, *upstream_series_name = package_and_upstream.split(":", 1)
        upstream_series_name = upstream_series_name[0] if upstream_series_name else series_name
        print(package_name, upstream_series_name)

        series = ubuntu.getSeries(name_or_version=series_name)
        upstream_series = ubuntu.getSeries(name_or_version=upstream_series_name)

        patched_sources = patches_archive.getPublishedSources(
            exact_match=True,
            source_name=package_name,
            status="Published",
            distro_series=series,
        )
        patched_version = patched_sources[0].source_package_version

        # Search for a new version in the Ubuntu repositories
        for pocket in ["Release", "Security", "Updates"]:

            upstream_sources = ubuntu_archive.getPublishedSources(
                exact_match=True,
                source_name=package_name,
                status="Published",
                pocket=pocket,
                distro_series=upstream_series,
            )

            if len(upstream_sources) <= 0:
                continue

            pocket_version = upstream_sources[0].source_package_version
            if apt_pkg.version_compare(pocket_version, patched_version) <= 0:
                continue

            pull_title = f"📦 Update {package_name} [{upstream_series_name}]"
            # if github_pull_exists(pull_title):
            #     continue

            base_branch = f"{package_name}-{upstream_series_name}"
            new_branch = f"bot/update/{package_name}-{upstream_series_name}"

                # Checkout the base branch
            current_repo.git.checkout(base_branch)
            # Create and checkout the new branch
            current_repo.git.checkout('-b', new_branch)


if __name__ == "__main__":
    main()

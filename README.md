# Socio-technical analysis of the GNOME open source ecosystem on GitLab

## Contents

1. Introduction
2. Licensing
3. Usage of this repository
4. How to run the scripts
    1. Using your own environment
    2. Using the Nix flake (recommended)
    3. Using the Nix shell

## Introduction

*Keywords: Open source, Software ecosystem, Version control, GNOME, GitLab*

Open source project communities frequently establish ecosystems comprising collaborative projects or organisations. In the context of software development, the utilisation of social coding platforms such as GitHub and GitLab has become a prevalent practice, facilitating collaboration among team members in a distributed and decentralised manner. Each project is characterised by the presence of multiple interacting Git repositories, and a significant number of projects exhibit interconnectedness from both technical and social standpoints (with project interdependencies and contributors collaborating across different projects).

The study of open source ecosystems has become increasingly important due to the growing influence of open source software in the technology sector. However, despite their importance, many analyses have historically focused on technical or economic aspects, often overlooking the intricate socio-technical dynamics that govern such ecosystems. It is imperative to comprehend these dynamics in order to gain insights into the processes by which collaboration emerges, the manner in which communities are structured, and the distribution of work among contributors. Large ecosystems offer a conducive environment for this type of analysis due to their longevity, size, and diversity of projects.

The objective of this study is to improve understanding of how a large open-source ecosystem functions, through an empirical analysis of a case study. The focal point of this analysis is the GNOME project, which is hosted on GitLab1 . The GNOME project oversees a wide range of well-known Linux desktop environment projects, including GTK, GStreamer, Mutter, Nautilus and many others. By analysing the historical activities recorded in GitLab repositories, we characterise the collaboration behaviours of contributors and the structural organisation of the ecosystem.

This analysis is conducted by utilising historical collaboration data that is collected through the utilisation of the GitLab REST API. The primary focus of this analysis is event activities, including commits, issues, merge requests and comments, in addition to information pertaining to contributor roles within the projects. DuckDB is used for data manipulation, facilitating efficient querying and aggregation of large JSON datasets, circumventing the necessity for an intermediary database system. The collated data, organised in JSON files, as well as the code that was used in our analyses can be found for reproducibility in this repository.

## Licensing

The scripts contained in the `scripts/` directory are licensed under the GNU General Public License v3.0.

You must additionally provide visible credit to the original author (Arnaud Moreau) and provide a link to this repository ([https://github.com/Nephty/thesis](https://github.com/Nephty/thesis)) in any public use or distribution of this software, including modified versions.

The data contained in the `data/` directory was retrieved through the GitLab API. While the API requires users to have a GitLab account, no special permissions or access grants were needed; this information is publicly available to any user authanticated using their GitLab account.

## Usage of this repository

This repository is structured as follows:

- `data/` contains the data extracted using the GitLab API.
  - `events/` contains the fetched events. It contains one JSON file per considered project which use the nomenclature `filtered-events-<PROJECT_NAME>.json`.
  - `members/` contains the fetched members. It contains one JSON file per considered project which use the nomenclature `filtered-members-<PROJECT_NAME>.json`.
  - `projects.json` contains the fetched projects. They are grouped in this single JSON file.
- `scripts/` contains one directory per section of chapter 3. Each directory contains the necessary code for reproduction of the queries and plots of its corresponding section.
- `flake.nix` and `flake.lock` allow us to enter a development environment using a Nix flake for easy reproducibility.
- `shell.nix` serves the same purpose but uses a Nix shell.

## How to run the scripts

There are three methods to run the scripts.

1. Use your own Python environment.
2. Enter a pre-defined development environment using Nix flakes (recommended).
3. Enter a pre-defined development environment using Nix shells.

### Installing Nix and NixOS

The second and third methods require the user to have the Nix package manager installed. You can either use the Nix package manager on its own, or use NixOS which itself uses Nix at its core.

Learn [how to install Nix](https://nixos.wiki/wiki/Nix_Installation_Guide) or [how to install NixOS](https://nixos.wiki/wiki/NixOS_Installation_Guide).

The second method also requires the user to have Nix flakes enabled.

Learn [how to enable Nix flakes](https://nixos.wiki/wiki/flakes).

### Using your own environment

Install the dependencies using `pip` via:

```bash
pip install -r requirements.txt
```

Run the scripts located in the `scripts/` directory.

### Using the Nix flake (recommended)

With Nix flakes enabled, enter the development environment using:

```bash
nix develop
```

Run the scripts located in the `scripts/` directory.

### Using the Nix shell

Enter the development environment using:

```bash
nix-shell
```

Run the scripts located in the `scripts/` directory.
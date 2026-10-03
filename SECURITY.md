# Security and Responsible Disclosure

## Scope

This repository is under active development. Security reports are especially valuable for:

- exposed credentials, secrets, or sensitive configuration;
- dependency vulnerabilities and unsafe supply-chain behavior;
- unsafe GitHub Actions or workflow behavior;
- data-integrity or persistence vulnerabilities;
- unintended code-execution or runtime-boundary behavior.

## Private reporting

Please report suspected vulnerabilities privately through GitHub's **Security** → **Report a vulnerability** mechanism when private vulnerability reporting is enabled for this repository.

If private vulnerability reporting is unavailable, use the private contact mechanism configured in the repository's GitHub security settings. Do not place credentials, private data, or actionable exploit details in a public issue.

## What to include

Where safe to do so, include:

- a concise description of the vulnerability;
- affected file, component, or workflow;
- reproducible steps or a minimal proof of concept;
- affected commit or branch;
- potential impact and relevant mitigations.

Please avoid submitting real credentials, personal data, or destructive proof-of-concept material.

## Public issues

Use ordinary GitHub issues for non-sensitive bugs, documentation problems, and feature requests. If a public issue may contain security-sensitive information, keep the report private instead.

## Supported development line

`main` is the canonical project state. Unmerged branches and pull requests are development candidates and are not treated as released functionality.

## Responsible use

This project is provided for research, engineering, and educational purposes. Users remain responsible for securing their environments, protecting credentials, complying with applicable laws and regulations, and evaluating the risks of any software or output they use.

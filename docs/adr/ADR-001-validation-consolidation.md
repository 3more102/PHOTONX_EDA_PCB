# ADR-001: Consolidate validation through adapters

Status: accepted

The repository contains legacy validation, checks, rule registries, DRC, ERC and newer validation pipelines. Removing public APIs abruptly would create unnecessary breakage.

Decision: retain existing validators and normalize their outputs through validation_bridge. New release gates consume normalized issue counts where practical.

Consequence: migration can be incremental and backwards compatible.

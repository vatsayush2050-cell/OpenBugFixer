#!/usr/bin/env python3
"""
OpenBugFixer Agent — Autonomous open-source bug fixer for Hacktoberfest.
Scans GitHub repos for issues, analyzes code, and opens PRs with fixes.
"""

import argparse
import sys
from agent.orchestrator import BugFixerOrchestrator
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="OpenBugFixer Agent — AI-powered open-source bug fixer"
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="GitHub repo in owner/repo format (e.g. python/cpython)",
    )
    parser.add_argument(
        "--issue",
        type=int,
        help="Specific issue number to fix (optional; agent picks one if omitted)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and generate fix but do NOT open a real PR",
    )
    parser.add_argument(
        "--max-issues",
        type=int,
        default=5,
        help="Max issues to scan when no specific issue is given (default: 5)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="openrouter/mistralai/mistral-7b-instruct",
        help="OpenRouter model string to use for code analysis",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    settings = Settings(model=args.model, dry_run=args.dry_run)

    logger.info("🤖 OpenBugFixer Agent starting up")
    logger.info(f"   Model  : {settings.model}")
    logger.info(f"   Dry run: {settings.dry_run}")

    if not args.repo:
        logger.error("--repo is required. Example: --repo owner/repo")
        sys.exit(1)

    orchestrator = BugFixerOrchestrator(settings)

    try:
        result = orchestrator.run(
            repo_full_name=args.repo,
            issue_number=args.issue,
            max_issues=args.max_issues,
        )
        if result:
            logger.info(f"✅ Done! {result}")
        else:
            logger.warning("Agent finished but no actionable fix was produced.")
    except KeyboardInterrupt:
        logger.info("Aborted by user.")
    except Exception as exc:
        logger.error(f"Fatal error: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
learn_to_write — Scrape X accounts, analyze writing style, generate a Claude Scale.

Usage:
    python main.py scrape <handle> [--max-posts 200] [--visible]
    python main.py analyze <handle> <data-file>
    python main.py generate <handle> <profile-file>
    python main.py apply <scale-file> <text>
    python main.py pipeline <handle> [--max-posts 200] [--visible]
"""

import click
from pathlib import Path

from src.scraper import scrape_account, save_posts
from src.analyzer import analyze_style, load_posts, save_profile
from src.scale_generator import generate_scale, save_scale, apply_scale


@click.group()
def cli():
    """Learn to write like anyone — powered by scraping + Claude."""
    pass


@cli.command()
@click.argument("handle")
@click.option("--max-posts", default=200, help="Max posts to scrape")
@click.option("--visible", is_flag=True, help="Show the browser window")
def scrape(handle: str, max_posts: int, visible: bool):
    """Scrape posts from an X account."""
    posts = scrape_account(handle, max_posts=max_posts, headless=not visible)
    save_posts(handle, posts)


@cli.command()
@click.argument("handle")
@click.argument("data_file", type=click.Path(exists=True))
def analyze(handle: str, data_file: str):
    """Analyze scraped posts and create a style profile."""
    posts = load_posts(data_file)
    profile = analyze_style(posts)
    save_profile(handle, profile)

    # Print summary
    click.echo(f"\n--- Style Profile for @{handle} ---")
    click.echo(f"Posts analyzed: {profile['total_posts']}")
    click.echo(f"Avg post length: {profile['length']['avg_words']} words")
    click.echo(f"Line breaks: {profile['structure']['line_breaks_pct']}% of posts")
    click.echo(f"Question openers: {profile['structure']['question_opener_pct']}%")
    click.echo(f"Informal tone: {profile['tone']['informal_pct']}%")
    click.echo(f"Starts lowercase: {profile['formatting']['starts_lowercase_pct']}%")
    click.echo(f"Top words: {', '.join(w for w, _ in profile['vocabulary']['top_words'][:10])}")
    if profile["topics"]:
        click.echo(f"Top hashtags: {', '.join(profile['topics'][:10])}")


@cli.command()
@click.argument("handle")
@click.argument("profile_file", type=click.Path(exists=True))
@click.option("--model", default="claude-sonnet-4-20250514", help="Claude model to use")
def generate(handle: str, profile_file: str, model: str):
    """Generate a Claude Scale from a style profile."""
    import json
    with open(profile_file) as f:
        profile = json.load(f)
    scale_text = generate_scale(handle, profile, model=model)
    save_scale(handle, scale_text)


@cli.command()
@click.argument("scale_file", type=click.Path(exists=True))
@click.argument("text")
@click.option("--model", default="claude-sonnet-4-20250514", help="Claude model to use")
def apply(scale_file: str, text: str, model: str):
    """Rewrite text using a Claude Scale."""
    result = apply_scale(scale_file, text, model=model)
    click.echo("\n--- Rewritten Content ---")
    click.echo(result)


@cli.command()
@click.argument("handle")
@click.option("--max-posts", default=200, help="Max posts to scrape")
@click.option("--visible", is_flag=True, help="Show the browser window")
@click.option("--model", default="claude-sonnet-4-20250514", help="Claude model to use")
def pipeline(handle: str, max_posts: int, visible: bool, model: str):
    """Run the full pipeline: scrape -> analyze -> generate scale."""
    click.echo(f"=== Full Pipeline for @{handle} ===\n")

    # Step 1: Scrape
    click.echo("Step 1/3: Scraping posts...")
    posts = scrape_account(handle, max_posts=max_posts, headless=not visible)
    data_path = save_posts(handle, posts)

    # Step 2: Analyze
    click.echo("\nStep 2/3: Analyzing writing style...")
    profile = analyze_style(posts)
    profile_path = save_profile(handle, profile)

    # Step 3: Generate Scale
    click.echo("\nStep 3/3: Generating Claude Scale...")
    scale_text = generate_scale(handle, profile, model=model)
    scale_path = save_scale(handle, scale_text)

    click.echo(f"\n=== Done! ===")
    click.echo(f"Data:    {data_path}")
    click.echo(f"Profile: {profile_path}")
    click.echo(f"Scale:   {scale_path}")
    click.echo(f"\nTo use the scale:")
    click.echo(f'  python main.py apply "{scale_path}" "Your text here"')


if __name__ == "__main__":
    cli()

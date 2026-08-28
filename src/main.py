import os
import sys
import json
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv

# Rich for TUI
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import print as rprint

# Local imports
from src.ai_engine import AIEngine
from src.recommender import Recommender
from src.schemas import ArtistIntelligence, RecommendationResult

load_dotenv()

console = Console()

def print_header():
    console.print(Panel.fit("[bold cyan]SEKERON AI INTERN ASSESSMENT[/]\n[white]Stage 3: Artist Intelligence & Recommendation System[/]", border_style="cyan"))

def analyze_artists(api_key: str):
    engine = AIEngine(api_key)
    artists_dir = Path("data/artists")
    
    if not artists_dir.exists():
        console.print("[red]Error: data/artists/ directory not found.[/red]")
        return
        
    artist_folders = [f for f in artists_dir.iterdir() if f.is_dir()]
    if not artist_folders:
        console.print("[red]No artist folders found in data/artists/.[/red]")
        return

    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("[cyan]Processing Artist Portfolios (Media + Text)...", total=len(artist_folders))
        
        for folder in artist_folders:
            category = "photographer"
            if "m0" in folder.name.lower() or "music" in folder.name.lower(): category = "musician"
            elif "v0" in folder.name.lower() or "video" in folder.name.lower() or "edit" in folder.name.lower(): category = "video_editor"
            elif "p0" in folder.name.lower() or "photo" in folder.name.lower(): category = "photographer"
                
            progress.update(task, description=f"[cyan]Analyzing {folder.name} ({category})...")
            
            # Process using Gemini
            record = engine.process_artist(str(folder), category)
            results.append(record.model_dump())
            
            # Avoid Google Free Tier Rate Limits (15 Requests Per Minute)
            time.sleep(4)
            
            progress.advance(task)

    out_file = Path("outputs/artist_intelligence.jsonl")
    out_file.parent.mkdir(exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
            
    console.print(f"[bold green]✔ Successfully generated evidence-backed intelligence for {len(results)} artists.[/bold green]")
    console.print(f"[white]Output saved to: {out_file}[/white]")

    # Demo output for the recruiter
    if results:
        # Find one that actually worked instead of a fallback
        sample = next((r for r in results if r.get('category_specific_dimensions')), results[0])
        table = Table(title=f"Sample Intelligence Extract: {sample['artist_id']}")
        table.add_column("Dimension", style="cyan")
        table.add_column("Assessment", style="white")
        table.add_column("Evidence Cited", style="magenta")
        table.add_column("Confidence", style="green")
        
        for dim in sample.get('category_specific_dimensions', []):
            table.add_row(dim['dimension_name'], dim['assessment'][:50]+"...", dim['evidence_citation'], dim['confidence'])
            
        console.print(table)


def generate_recommendations(api_key: str):
    engine = Recommender(api_key)
    
    intel_file = Path("outputs/artist_intelligence.jsonl")
    briefs_dir = Path("data/briefs")
    
    if not intel_file.exists():
        console.print("[red]Run analysis first. artist_intelligence.jsonl not found.[/red]")
        return
        
    records = []
    with open(intel_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(ArtistIntelligence.model_validate_json(line))
            
    brief_files = [f for f in briefs_dir.glob("*.txt") if f.name != "follow_up.txt"]
    if not brief_files:
        console.print("[red]No brief files found in data/briefs/.[/red]")
        return

    results = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Matching Hirer Intents to Artist Evidence...", total=len(brief_files))
        
        for brief in brief_files:
            with open(brief, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            rec = engine.generate_recommendation(brief.name, text, records)
            results.append(rec.model_dump())
            time.sleep(2)  # Avoid rate limits
            progress.advance(task)
            
    out_file = Path("outputs/recommendations.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    console.print(f"[bold green]✔ Recommendations generated for {len(results)} briefs.[/bold green]")

    # Demo output
    if results:
        sample = results[0]
        console.print(Panel(f"[bold]Brief ID:[/] {sample['brief_id']}\n[bold]Intent:[/] {sample['interpreted_intent']}", title="Sample Recommendation"))
        for rank in sample['initial_top_two']:
            console.print(f" [yellow]Rank {rank['rank']}: {rank['artist_id']}[/yellow] - {rank['match_reasoning'][:80]}...")


def rerank(api_key: str):
    engine = Recommender(api_key)
    
    intel_file = Path("outputs/artist_intelligence.jsonl")
    rec_file = Path("outputs/recommendations.json")
    update_file = Path("data/briefs/follow_up.txt")
    
    if not update_file.exists():
        console.print("[red]Follow-up text not found at data/briefs/follow_up.txt[/red]")
        return
        
    with open(update_file, "r", encoding="utf-8", errors="ignore") as f:
        update_text = f.read()
        
    records = []
    with open(intel_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(ArtistIntelligence.model_validate_json(line))
            
    with open(rec_file, "r", encoding="utf-8") as f:
        recs = json.load(f)
        
    if not recs:
        return
        
    orig_rec = RecommendationResult.model_validate(recs[0])
    
    with console.status("[cyan]Processing follow-up constraints and re-ranking..."):
        updated = engine.rerank_recommendation(orig_rec.brief_id, orig_rec, update_text, records)
        
    out_file = Path("outputs/updated_recommendation.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(updated.model_dump(), f, indent=2)
        
    console.print(f"[bold green]✔ Re-ranking complete.[/bold green]")
    console.print(Panel(f"[bold]What changed:[/] {updated.what_changed_and_why}", title="Re-Rank Rationale", border_style="magenta"))


if __name__ == "__main__":
    print_header()
    
    parser = argparse.ArgumentParser(description="Sekeron AI Pipeline")
    parser.add_argument("--mode", choices=["analyze_artists", "recommend", "rerank", "demo_all"], required=True)
    args = parser.parse_args()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[bold red]ERROR: GEMINI_API_KEY environment variable not set.[/bold red]")
        sys.exit(1)
        
    if args.mode == "analyze_artists":
        analyze_artists(api_key)
    elif args.mode == "recommend":
        generate_recommendations(api_key)
    elif args.mode == "rerank":
        rerank(api_key)
    elif args.mode == "demo_all":
        analyze_artists(api_key)
        generate_recommendations(api_key)
        rerank(api_key)

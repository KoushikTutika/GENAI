#!/usr/bin/env python3
"""Command-line interface for InfoChatAgent"""

import click
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.infochat_agent.scrape import WebScraper, save_docstore
from src.infochat_agent.index import build_index_from_docstore
from src.infochat_agent.rag import RAGPipeline
from src.infochat_agent.config import config

console = Console()

@click.group()
def cli():
    """InfoChatAgent: Web Scraping + RAG Agent"""
    pass

@cli.command()
@click.option('--url', multiple=True, help='URLs to scrape')
@click.option('--html-dir', help='Directory containing HTML files')
@click.option('--output', default=config.default_docstore, help='Output docstore path')
@click.option('--follow-links', is_flag=True, help='Follow StackOverflow question links')
@click.option('--link-limit', default=10, help='Maximum links to follow')
def scrape(url, html_dir, output, follow_links, link_limit):
    """Scrape web pages or HTML files"""
    scraper = WebScraper()
    documents = []
    
    if url:
        console.print(f"[blue]Scraping {len(url)} URLs...[/blue]")
        documents = scraper.scrape_multiple(list(url), follow_links, link_limit)
    elif html_dir:
        console.print(f"[blue]Scraping HTML files from {html_dir}...[/blue]")
        documents = scraper.scrape_html_files(html_dir)
    else:
        console.print("[red]Error: Provide either --url or --html-dir[/red]")
        return
    
    if documents:
        save_docstore(documents, output)
        console.print(f"[green]Saved {len(documents)} documents to {output}[/green]")
        
        # Show summary
        table = Table(title="Scraped Documents")
        table.add_column("Title", style="cyan")
        table.add_column("URL", style="blue")
        table.add_column("Length", justify="right", style="magenta")
        
        for doc in documents[:10]:  # Show first 10
            table.add_row(
                doc['title'][:50] + "..." if len(doc['title']) > 50 else doc['title'],
                doc['url'][:60] + "..." if len(doc['url']) > 60 else doc['url'],
                str(doc['length'])
            )
        
        console.print(table)
        if len(documents) > 10:
            console.print(f"[dim]... and {len(documents) - 10} more documents[/dim]")
    else:
        console.print("[red]No documents scraped[/red]")

@cli.command()
@click.option('--docstore', default=config.default_docstore, help='Input docstore path')
@click.option('--index-dir', default=config.default_index_dir, help='Output index directory')
def index(docstore, index_dir):
    """Build vector index from docstore"""
    if not os.path.exists(docstore):
        console.print(f"[red]Error: Docstore {docstore} not found[/red]")
        return
    
    console.print(f"[blue]Building index from {docstore}...[/blue]")
    
    try:
        vector_index = build_index_from_docstore(docstore, index_dir)
        console.print(f"[green]Index built successfully and saved to {index_dir}[/green]")
        console.print(f"[dim]Index contains {len(vector_index.metadata)} chunks[/dim]")
    except Exception as e:
        console.print(f"[red]Error building index: {e}[/red]")

@cli.command()
@click.option('--index-dir', default=config.default_index_dir, help='Index directory')
@click.option('--question', prompt='Question', help='Question to ask')
@click.option('--model', help='OpenAI model to use (if available)')
@click.option('--top-k', default=config.top_k, help='Number of results to retrieve')
@click.option('--no-llm', is_flag=True, help='Use extractive answers only')
def ask(index_dir, question, model, top_k, no_llm):
    """Ask questions against the index"""
    if not os.path.exists(index_dir):
        console.print(f"[red]Error: Index directory {index_dir} not found[/red]")
        return
    
    try:
        # Initialize RAG pipeline
        rag = RAGPipeline(index_dir, model)
        
        console.print(f"[blue]Searching for: {question}[/blue]")
        
        # Get answer
        response = rag.ask(question, use_llm=not no_llm, top_k=top_k)
        
        # Display answer
        console.print(Panel(response['answer'], title="Answer", border_style="green"))
        
        # Display insights
        if response['insights']['common_terms']:
            console.print("\n[bold]Top Insights:[/bold]")
            terms_str = ", ".join([f"{term} ({count})" for term, count in response['insights']['common_terms'][:5]])
            console.print(f"Common terms: {terms_str}")
            console.print(f"Sources: {response['insights']['sources_count']}")
        
        # Display sources
        if response['sources']:
            console.print("\n[bold]Sources:[/bold]")
            for i, (title, url) in enumerate(response['sources'], 1):
                console.print(f"{i}. {title}")
                console.print(f"   [dim]{url}[/dim]")
        
        # Display passages
        if response['passages']:
            console.print("\n[bold]Relevant Passages:[/bold]")
            for i, passage in enumerate(response['passages'][:3], 1):
                console.print(f"\n[cyan]{i}. {passage['source']} (score: {passage['score']:.3f})[/cyan]")
                console.print(f"[dim]{passage['text']}[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == '__main__':
    cli()
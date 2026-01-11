"""
API Response Formatter with Rich Components
Clean, reusable formatting functions without infinite loops
Author: @AkshatBhatt-786
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax
from rich.columns import Columns
from rich import box
import json
from datetime import datetime
from typing import Dict, Any, Optional
import requests

console = Console()

# ==================== FORMATTING COMPONENTS ====================

def format_request_table(method: str, url: str, data: Optional[Dict] = None, 
                        headers: Optional[Dict] = None) -> Table:
    """Format request details in a table"""
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    table.add_column("Key", style="bold magenta", width=15)
    table.add_column("Value", style="white")
    
    table.add_row("Method", f"[bold green]{method}[/bold green]")
    table.add_row("URL", f"[underline blue]{url}[/underline blue]")
    table.add_row("Time", datetime.now().strftime("%H:%M:%S"))
    
    if headers:
        headers_str = "\n".join([f"{k}: [dim]{v}[/dim]" for k, v in headers.items()])
        table.add_row("Headers", headers_str)
    
    if data:
        data_json = json.dumps(data, indent=2)
        table.add_row("Body", f"[dim]{data_json}[/dim]")
    
    return table

def format_response_tree(response: requests.Response) -> Tree:
    """Format response as a tree structure"""
    tree = Tree(f"[bold]Response: [green]{response.status_code}[/green][/bold]")
    
    # Basic info branch
    info_branch = tree.add("Basic Info")
    info_branch.add(f"[cyan]Status:[/cyan] [bold]{response.status_code} {response.reason}[/bold]")
    info_branch.add(f"[cyan]Time:[/cyan] {response.elapsed.total_seconds():.3f}s")
    info_branch.add(f"[cyan]Size:[/cyan] {len(response.content):,} bytes")
    
    # Headers branch
    if response.headers:
        headers_branch = tree.add("Headers")
        for key, value in sorted(response.headers.items()):
            headers_branch.add(f"[yellow]{key}:[/yellow] [white]{value}[/white]")
    
    # Body branch
    body_branch = tree.add("Body")
    try:
        if response.headers.get('Content-Type', '').startswith('application/json'):
            body_json = response.json()
            body_str = json.dumps(body_json, indent=2)
            body_branch.add(Syntax(body_str, "json", theme="monokai", word_wrap=True))
        else:
            body_branch.add(f"[white]{response.text[:200]}...[/white]" if len(response.text) > 200 else response.text)
    except:
        body_branch.add("[red]Could not parse body[/red]")
    
    return tree

def format_status_panel(status_code: int, data: Dict) -> Panel:
    """Format status summary in a panel"""
    if 200 <= status_code < 300:
        color = "green"
        emoji = "✅"
        title = "SUCCESS"
    elif 400 <= status_code < 500:
        color = "yellow"
        emoji = "⚠️"
        title = "CLIENT ERROR"
    else:
        color = "red"
        emoji = "❌"
        title = "SERVER ERROR"
    
    status_text = f"[bold {color}]{emoji} {title} ({status_code})[/bold {color}]"
    
    # Create info lines
    info_lines = []
    
    if status_code == 201:
        info_lines.append("[green]✓ Resource created successfully[/green]")
        if 'user' in data:
            info_lines.append(f"[cyan]User ID:[/cyan] {data['user'].get('id', 'N/A')}")
    elif status_code == 200:
        info_lines.append("[green]✓ Request successful[/green]")
        if 'access_token' in data:
            info_lines.append(f"[cyan]Token:[/cyan] {data['access_token'][:30]}...")
    elif status_code == 400:
        info_lines.append(f"[red]✗ {data.get('error', 'Bad Request')}[/red]")
    elif status_code == 401:
        info_lines.append("[red]✗ Unauthorized - Invalid credentials[/red]")
    elif status_code == 404:
        info_lines.append("[yellow]⚠ Endpoint not found[/yellow]")
    
    if 'message' in data:
        info_lines.append(f"[white]💬 {data['message']}[/white]")
    
    content = "\n".join(info_lines)
    return Panel(content, title=status_text, border_style=color)

def format_key_value_table(title: str, data: Dict, key_style: str = "cyan") -> Panel:
    """Format key-value pairs in a table panel"""
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Key", style=f"bold {key_style}", width=20)
    table.add_column("Value", style="white")
    
    for key, value in data.items():
        if isinstance(value, dict):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)
        table.add_row(key, value_str)
    
    return Panel(table, title=f"[bold]{title}[/bold]")

# ==================== TEST FUNCTIONS ====================

def test_endpoint(method: str, url: str, data: Optional[Dict] = None, 
                 headers: Optional[Dict] = None, description: str = ""):
    
    if description:
        console.print(Panel(f"[bold cyan]{description}[/bold cyan]", border_style="cyan"))
    
    # Request
    request_table = format_request_table(method, url, data, headers)
    console.print(Panel(request_table, title="[bold]Request[/bold]", border_style="blue"))
    
    console.print("\n[dim]Sending request...[/dim]\n")
    
    # Make request
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            console.print(f"[red]Unsupported method: {method}[/red]")
            return None
        
        # Response tree
        response_tree = format_response_tree(response)
        console.print(Panel(response_tree, title="[bold]Response[/bold]", border_style="yellow"))
        
        # Status panel
        try:
            response_data = response.json() if response.text else {}
        except:
            response_data = {}
        
        status_panel = format_status_panel(response.status_code, response_data)
        console.print(status_panel)
        
        return response
        
    except requests.exceptions.ConnectionError:
        error_panel = Panel(
            "[bold red]Connection Failed[/bold red]\n"
            "[yellow]Server is not running or unreachable.[/yellow]\n"
            "Run: [cyan]python run.py[/cyan]",
            border_style="red"
        )
        console.print(error_panel)
    except Exception as e:
        error_panel = Panel(
            f"[bold red]Request Failed[/bold red]\n[yellow]{str(e)}[/yellow]",
            border_style="red"
        )
        console.print(error_panel)
    
    return None

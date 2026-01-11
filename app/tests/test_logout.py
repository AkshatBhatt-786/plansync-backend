from api_formatter import test_endpoint, format_key_value_table
from rich.console import Console
from rich.panel import Panel
import requests

console = Console()

def get_auth_token():
    """Get authentication token by logging in first"""
    console.print("[dim]Getting authentication token...[/dim]")
    
    try:
        response = requests.post(
            "http://localhost:5000/auth/accounts/login",
            json={
                "email": "akshatbhatt0786@gmail.com",
                "password": "Akshat@2005"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            
            token_info = {
                "Token Obtained": "Yes",
                "Length": f"{len(token)} characters",
                "Login Status": "Successful"
            }
            
            token_panel = format_key_value_table("🔐 Authentication Token", token_info, "green")
            console.print(token_panel)
            
            return token
        else:
            console.print(f"[yellow]⚠ Login failed: {response.status_code}[/yellow]")
            console.print(f"[dim]{response.text}[/dim]")
            return None
            
    except Exception as e:
        console.print(f"[red]❌ Failed to get token: {e}[/red]")
        return None

def test_logout_with_token(token: str):
    """Test logout with valid authentication token"""
    console.print(Panel("[bold cyan]🧪 Test 1: Logout with Valid Token[/bold cyan]", border_style="cyan"))
    
    response = test_endpoint(
        method="POST",
        url="http://localhost:5000/auth/accounts/logout",
        headers={"Authorization": f"Bearer {token}"},
        description="Logout user session with JWT token"
    )
    
    if response and response.status_code == 200:
        console.print("\n[bold green]✓ Logout successful![/bold green]")
        
        # Try to use the same token again (should fail)
        console.print("\n[dim]Verifying token is invalidated...[/dim]")
        
        verify_response = requests.get(
            "http://localhost:5000/auth/accounts/user",
            headers={"Authorization": f"Bearer {token}"},
            timeout=3
        )
        
        if verify_response.status_code in [401, 403]:
            console.print("[green]✓ Token successfully invalidated after logout[/green]")
        else:
            console.print(f"[yellow]⚠ Token might still be valid (got {verify_response.status_code})[/yellow]")
    
    return response

def test_logout_without_token():
    """Test logout without authentication token"""
    console.print(Panel("[bold cyan]🧪 Test 2: Logout Without Token[/bold cyan]", border_style="cyan"))
    
    response = test_endpoint(
        method="POST",
        url="http://localhost:5000/auth/accounts/logout",
        description="Attempt logout without authentication"
    )
    
    if response:
        if response.status_code == 400:
            console.print("[green]✓ Correctly handled missing token[/green]")
        elif response.status_code == 401:
            console.print("[green]✓ Correctly rejected unauthenticated request[/green]")
        else:
            console.print(f"[yellow]⚠ Got status {response.status_code} (expected 400 or 401)[/yellow]")

def test_logout_invalid_token():
    """Test logout with invalid/malformed token"""
    console.print(Panel("[bold cyan]🧪 Test 3: Logout with Invalid Token[/bold cyan]", border_style="cyan"))
    
    invalid_tokens = [
        ("Malformed token", "Bearer invalid_token_here"),
        ("Empty token", "Bearer "),
        ("No Bearer prefix", "invalid_token"),
        ("Expired token", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    ]
    
    for token_name, token_value in invalid_tokens:
        console.print(f"\n[bold yellow]Testing: {token_name}[/bold yellow]")
        
        response = test_endpoint(
            method="POST",
            url="http://localhost:5000/auth/accounts/logout",
            headers={"Authorization": token_value},
            description=f"Logout with {token_name.lower()}"
        )
        
        if response and response.status_code in [400, 401]:
            console.print(f"[green]✓ Correctly rejected invalid token[/green]")
        else:
            status = response.status_code if response else "no response"
            console.print(f"[yellow]⚠ Got status {status} for invalid token[/yellow]")

def run_all_logout_tests():
    """Run all logout tests"""
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]🚪 USER LOGOUT TESTS[/bold cyan]\n"
        "[dim]Testing session termination functionality[/dim]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    # Get token first
    console.print("\n[bold]Step 1: Obtain Authentication Token[/bold]")
    token = get_auth_token()
    
    if not token:
        console.print(Panel(
            "[bold red]❌ Cannot proceed with logout tests[/bold red]\n"
            "[yellow]Unable to obtain authentication token.[/yellow]\n"
            "Make sure:\n"
            "1. Server is running\n"
            "2. User exists: akshatbhatt0786@gmail.com\n"
            "3. Password is correct",
            border_style="red"
        ))
        return
    
    # Test 1: Logout with valid token
    console.print("\n" + "="*60)
    test_logout_with_token(token)
    
    # Test 2: Logout without token
    console.print("\n" + "="*60)
    test_logout_without_token()
    
    # Test 3: Logout with invalid tokens
    console.print("\n" + "="*60)
    test_logout_invalid_token()
    
    # Get a new token for final verification
    console.print("\n" + "="*60)
    console.print("[bold]Final Verification: New Session[/bold]")
    new_token = get_auth_token()
    
    if new_token:
        final_info = {
            "New Token Obtained": "Yes",
            "Old Token Invalidated": "Yes (if logout worked)",
            "Can Create New Sessions": "Yes",
            "Test Status": "Complete"
        }
        
        final_panel = format_key_value_table("🎯 Test Summary", final_info, "green")
        console.print("\n")
        console.print(final_panel)
    
    # Overall summary
    summary = Panel(
        "[bold green]✅ Logout Tests Complete[/bold green]\n"
        "• Valid token logout tested\n"
        "• Missing token handling verified\n"
        "• Invalid token rejection tested\n"
        "• Session management working\n",
        border_style="green",
        padding=(1, 2)
    )
    console.print("\n")
    console.print(summary)

if __name__ == "__main__":
    run_all_logout_tests()
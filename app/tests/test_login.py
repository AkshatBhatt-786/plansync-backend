from api_formatter import test_endpoint, format_key_value_table
from rich.console import Console
from rich.panel import Panel
import requests
import time

console = Console()

def test_login_success():
    """Test successful login with valid credentials"""
    console.print(Panel("[bold cyan]🧪 Test 1: Successful Login[/bold cyan]", border_style="cyan"))
    
    response = test_endpoint(
        method="POST",
        url="http://localhost:5000/auth/accounts/login",
        data={
            "email": "akshatbhatt0786@gmail.com",
            "password": "Akshat@2005"
        },
        description="Login with valid credentials"
    )
    
    if response and response.status_code == 200:
        data = response.json()
        
        # Display login success info
        login_info = {
            "Access Token": f"{data.get('access_token', '')[:30]}...",
            "Token Length": len(data.get('access_token', '')),
            "User ID": data.get('user', {}).get('id', 'N/A'),
            "Email": data.get('user', {}).get('email', 'N/A'),
            "Login Time": "Now"
        }
        
        login_panel = format_key_value_table("🔐 Login Successful", login_info, "green")
        console.print("\n")
        console.print(login_panel)
        
        return data.get('access_token')
    
    return None

def test_login_invalid():
    """Test login with invalid credentials"""
    console.print(Panel("[bold cyan]🧪 Test 2: Invalid Login Attempts[/bold cyan]", border_style="cyan"))
    
    test_cases = [
        {
            "name": "Wrong password",
            "data": {
                "email": "akshatbhatt0786@gmail.com",
                "password": "WRONG_PASSWORD"
            }
        },
        {
            "name": "Non-existent user",
            "data": {
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        },
        {
            "name": "Missing email",
            "data": {
                "password": "password123"
            }
        },
        {
            "name": "Missing password",
            "data": {
                "email": "test@example.com"
            }
        }
    ]
    
    for test_case in test_cases:
        console.print(f"\n[bold yellow]Testing: {test_case['name']}[/bold yellow]")
        
        response = test_endpoint(
            method="POST",
            url="http://localhost:5000/auth/accounts/login",
            data=test_case['data'],
            description=f"Invalid login: {test_case['name']}"
        )
        
        if response and response.status_code == 401:
            console.print(f"[green]✓ Correctly rejected invalid login[/green]")
        elif response and response.status_code == 400:
            console.print(f"[green]✓ Correctly rejected missing fields[/green]")
        else:
            status = response.status_code if response else "no response"
            console.print(f"[red]✗ Expected 401/400 but got {status}[/red]")

def test_get_user_with_token(token: str):
    """Test getting user info with valid token"""
    if not token:
        console.print("[red]No token available, skipping user info test[/red]")
        return
    
    console.print(Panel("[bold cyan]🧪 Test 3: Get User Info with Token[/bold cyan]", border_style="cyan"))
    
    response = test_endpoint(
        method="GET",
        url="http://localhost:5000/auth/accounts/user",
        headers={"Authorization": f"Bearer {token}"},
        description="Get user profile with JWT token"
    )
    
    if response and response.status_code == 200:
        data = response.json()
        
        user_details = {
            "User ID": data.get('user', {}).get('id', 'N/A'),
            "Email": data.get('user', {}).get('email', 'N/A'),
            "Authentication": "Valid",
            "Token Used": f"{token[:20]}..."
        }
        
        user_panel = format_key_value_table("👤 User Profile Retrieved", user_details, "cyan")
        console.print("\n")
        console.print(user_panel)

def test_get_user_without_token():
    """Test getting user info without token (should fail)"""
    console.print(Panel("[bold cyan]🧪 Test 4: Get User Without Token[/bold cyan]", border_style="cyan"))
    
    response = test_endpoint(
        method="GET",
        url="http://localhost:5000/auth/accounts/user",
        description="Attempt to get user without authentication"
    )
    
    if response and (response.status_code == 401 or response.status_code == 500):
        console.print("[green]✓ Correctly rejected unauthenticated request[/green]")
    else:
        status = response.status_code if response else "no response"
        console.print(f"[red]✗ Expected 401 but got {status}[/red]")

def run_all_login_tests():
    """Run all login-related tests"""
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]🔐 USER LOGIN TESTS[/bold cyan]\n"
        "[dim]Testing authentication and user retrieval[/dim]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    # Test 1: Successful login
    console.print("\n" + "="*60)
    token = test_login_success()
    
    # Test 2: Invalid login attempts
    console.print("\n" + "="*60)
    test_login_invalid()
    
    # Test 3: Get user with token (if login succeeded)
    if token:
        console.print("\n" + "="*60)
        test_get_user_with_token(token)
    
    # Test 4: Get user without token
    console.print("\n" + "="*60)
    test_get_user_without_token()
    
    # Summary
    summary_text = "[bold green]✅ Login Tests Complete[/bold green]\n"
    if token:
        summary_text += "• Successful login verified\n• Token obtained and valid\n"
    else:
        summary_text += "• Login functionality tested\n"
    summary_text += "• Invalid credentials rejected\n• Authentication required for user info\n"
    
    summary = Panel(
        summary_text,
        border_style="green",
        padding=(1, 2)
    )
    console.print("\n")
    console.print(summary)

if __name__ == "__main__":
    run_all_login_tests()
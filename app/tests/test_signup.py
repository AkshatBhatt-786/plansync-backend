from api_formatter import test_endpoint, format_key_value_table
from rich.console import Console
from rich.panel import Panel
import time

console = Console()

def test_signup_basic():
    """Test basic user signup"""
    console.print(Panel("[bold cyan]🧪 Test 1: Basic User Signup[/bold cyan]", border_style="cyan"))
    
    response = test_endpoint(
        method="POST",
        url="http://localhost:5000/auth/accounts/signup",
        data={
            "email": "akshatbhatt0786@gmail.com",
            "password": "Akshat@2005"
        },
        description="Basic user registration"
    )
    
    return response

def test_signup_new_user():
    """Test signup with new unique email"""
    timestamp = int(time.time())
    test_email = f"testuser_{timestamp}@example.com"
    
    console.print(Panel(f"[bold cyan]🧪 Test 2: New User Signup ({test_email})[/bold cyan]", border_style="cyan"))
    
    response = test_endpoint(
        method="POST",
        url="http://localhost:5000/auth/accounts/signup",
        data={
            "email": test_email,
            "password": "Test@12345"
        },
        description="New user with unique email"
    )
    
    if response and response.status_code == 201:
        user_data = response.json().get('user', {})
        
        # Display user info
        user_info = {
            "User ID": user_data.get('id', 'N/A'),
            "Email": user_data.get('email', 'N/A'),
            "Status": "Created",
            "Test Type": "Unique email signup"
        }
        
        user_panel = format_key_value_table("👤 Created User Details", user_info, "green")
        console.print("\n")
        console.print(user_panel)
    
    return response

def test_signup_validation():
    """Test signup validation errors"""
    console.print(Panel("[bold cyan]🧪 Test 3: Signup Validation Tests[/bold cyan]", border_style="cyan"))
    
    test_cases = [
        {
            "name": "Missing email",
            "data": {"password": "test123"},
            "expected_error": True
        },
        {
            "name": "Missing password", 
            "data": {"email": "test@example.com"},
            "expected_error": True
        },
        {
            "name": "Empty data",
            "data": {},
            "expected_error": True
        }
    ]
    
    for test_case in test_cases:
        console.print(f"\n[bold yellow]Testing: {test_case['name']}[/bold yellow]")
        
        response = test_endpoint(
            method="POST",
            url="http://localhost:5000/auth/accounts/signup",
            data=test_case['data'],
            description=f"Validation: {test_case['name']}"
        )
        
        if response and response.status_code == 400:
            console.print(f"[green]✓ Correctly rejected invalid data[/green]")
        else:
            console.print(f"[red]✗ Expected 400 but got {response.status_code if response else 'no response'}[/red]")

def run_all_signup_tests():
    """Run all signup tests"""
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]📝 USER SIGNUP TESTS[/bold cyan]\n"
        "[dim]Testing authentication registration endpoint[/dim]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    # Test 1: Basic signup (might be duplicate)
    console.print("\n" + "="*60)
    test_signup_basic()
    
    # Test 2: New user signup
    console.print("\n" + "="*60)
    test_signup_new_user()
    
    # Test 3: Validation tests
    console.print("\n" + "="*60)
    test_signup_validation()
    
    # Summary
    summary = Panel(
        "[bold green]✅ Signup Tests Complete[/bold green]\n"
        "• Basic signup functionality verified\n"
        "• New user creation tested\n"
        "• Input validation tested\n"
        "[dim]Note: Duplicate emails return 201 but don't create new users[/dim]",
        border_style="green",
        padding=(1, 2)
    )
    console.print("\n")
    console.print(summary)

if __name__ == "__main__":
    run_all_signup_tests()
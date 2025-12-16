#!/usr/bin/env python3
"""
Script to check available models in DataRobot LLM Gateway catalog.
Usage:
    python check_available_models.py              # Interactive mode with provider selection
    python check_available_models.py --all       # Show all models (non-interactive)
    python check_available_models.py --provider <name>  # Show models from specific provider
    python check_available_models.py --html       # Generate HTML report
    python check_available_models.py --report     # Generate HTML report
"""

import os
import sys
import requests
import argparse
from dotenv import load_dotenv

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Load environment variables from .env file in backend directory
from pathlib import Path

# Get the project root directory and load .env from backend folder
project_root = Path(__file__).resolve().parent.parent
env_file_path = project_root / "backend" / ".env"

if env_file_path.exists():
    load_dotenv(env_file_path)
    print(f"{Colors.GREEN}[OK] Loaded environment from: {env_file_path}{Colors.END}\n")
else:
    print(f"{Colors.YELLOW}[!] No .env file found at: {env_file_path}{Colors.END}")
    print(f"{Colors.YELLOW}   Please create backend/.env with DATAROBOT_API_TOKEN{Colors.END}\n")

# Get DataRobot API token and endpoint from environment
datarobot_api_token = os.getenv("DATAROBOT_API_TOKEN")
datarobot_endpoint = os.getenv("DATAROBOT_ENDPOINT", "https://app.datarobot.com")

if not datarobot_api_token:
    raise ValueError(f"DATAROBOT_API_TOKEN not found in environment variables. Please set it in: {env_file_path}")

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_model_info(model, index):
    """Print formatted model information."""
    model_name = model.get('model', 'N/A')
    provider = model.get('provider', 'N/A')
    description = model.get('description', 'No description available')
    model_type = model.get('type', 'N/A')
    is_active = model.get('isActive', 'Unknown')
    license_info = model.get('license', 'N/A')
    
    # Status indicator
    status_icon = "[ACTIVE]" if is_active else "[INACTIVE]"
    status_color = Colors.GREEN if is_active else Colors.RED

    print(f"{Colors.CYAN}{Colors.BOLD}+-- Model #{index + 1} {status_icon}{Colors.END}")
    print(f"{Colors.CYAN}|{Colors.END}")
    print(f"{Colors.CYAN}+--{Colors.END} {Colors.BLUE}{'Name:':<10}{Colors.END}{Colors.GREEN}{Colors.BOLD}{model_name}{Colors.END}")
    print(f"{Colors.CYAN}+--{Colors.END} {Colors.BLUE}{'Provider:':<10}{Colors.END}{Colors.YELLOW}{provider}{Colors.END}")
    print(f"{Colors.CYAN}+--{Colors.END} {Colors.BLUE}{'Type:':<10}{Colors.END}{Colors.CYAN}{model_type}{Colors.END}")
    print(f"{Colors.CYAN}+--{Colors.END} {Colors.BLUE}{'License:':<10}{Colors.END}{license_info}")
    print(f"{Colors.CYAN}+--{Colors.END} {Colors.BLUE}{'Status:':<10}{Colors.END}{status_color}{'Active' if is_active else 'Inactive'}{Colors.END}")
    
    print(f"{Colors.CYAN}+--{Colors.END} {Colors.BLUE}{'Description:':<10}{Colors.END}")

    # Format description with word wrapping
    if description and description != 'No description available':
        desc_lines = []
        words = description.split()
        current_line = ""
        for word in words:
            if len(current_line + " " + word) < 60:
                current_line += " " + word if current_line else word
            else:
                desc_lines.append(current_line)
                current_line = word
        if current_line:
            desc_lines.append(current_line)

        for i, line in enumerate(desc_lines):
            prefix = f"{Colors.CYAN}|{Colors.END}  " if i == 0 else f"{Colors.CYAN}|{Colors.END}  "
            print(f"{prefix}{line}")
    else:
        print(f"{Colors.CYAN}|{Colors.END}  {Colors.YELLOW}No description available{Colors.END}")

    print(f"{Colors.CYAN}+--{Colors.END}")
    print()

def get_available_providers(models):
    """Extract unique providers from the models list."""
    providers = set()
    for model in models:
        provider = model.get('provider', 'Unknown')
        if provider and provider != 'N/A':
            providers.add(provider)
    
    # Sort providers for consistent display
    return sorted(list(providers))

def display_provider_menu(providers):
    """Display a numbered menu of available providers."""
    print(f"{Colors.HEADER}{Colors.BOLD}Available Providers:{Colors.END}")
    print()
    
    for i, provider in enumerate(providers, 1):
        print(f"  {Colors.CYAN}{i:2d}.{Colors.END} {Colors.YELLOW}{provider}{Colors.END}")
    
    print(f"  {Colors.CYAN}{len(providers) + 1:2d}.{Colors.END} {Colors.GREEN}All Providers{Colors.END} {Colors.BLUE}(show everything){Colors.END}")
    print()

def get_user_provider_choice(providers):
    """Get user's provider choice with input validation."""
    while True:
        try:
            choice = input(f"{Colors.BLUE}Select provider [1-{len(providers) + 1}]: {Colors.END}").strip()
            
            if not choice:
                print(f"{Colors.YELLOW}[!] Please enter a number{Colors.END}")
                continue
                
            # Try to parse as number
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(providers) + 1:
                    if choice_num == len(providers) + 1:
                        return "all"
                    return providers[choice_num - 1]
                else:
                    print(f"{Colors.RED}[!] Please enter a number between 1 and {len(providers) + 1}{Colors.END}")
                    continue
            except ValueError:
                # Try to match by provider name (case-insensitive)
                choice_lower = choice.lower()
                for provider in providers:
                    if provider.lower() == choice_lower:
                        return provider
                
                print(f"{Colors.RED}[!] Invalid choice. Please enter a number or provider name{Colors.END}")
                continue
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[!] Operation cancelled by user{Colors.END}")
            sys.exit(0)
        except EOFError:
            print(f"\n{Colors.YELLOW}[!] No input available. Using 'All Providers' mode{Colors.END}")
            return "all"

def filter_models_by_provider(models, selected_provider):
    """Filter models based on selected provider."""
    if selected_provider == "all":
        return models
    
    filtered_models = []
    for model in models:
        provider = model.get('provider', 'Unknown')
        if provider == selected_provider:
            filtered_models.append(model)
    
    return filtered_models

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Check available models in DataRobot LLM Gateway catalog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check_available_models.py              # Interactive mode with provider selection
  python check_available_models.py --all       # Show all models (non-interactive)
  python check_available_models.py --provider OpenAI  # Show OpenAI models only
  python check_available_models.py --html      # Interactive + HTML report
  python check_available_models.py --all --html # All models + HTML report
        """
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='Show all models (non-interactive mode)')
    parser.add_argument('--provider', type=str, 
                       help='Show models from specific provider only')
    parser.add_argument('--html', action='store_true', 
                       help='Generate HTML report')
    parser.add_argument('--report', action='store_true', 
                       help='Generate HTML report (alias for --html)')
    
    return parser.parse_args()

def fetch_models_catalog(datarobot_api_token, datarobot_endpoint):
    """Fetch models from DataRobot catalog."""
    # Remove /api/v2 suffix if present for the genai endpoint
    base_url = datarobot_endpoint.replace("/api/v2", "")
    catalog_url = f"{base_url}/genai/llmgw/catalog/"

    print(f"{Colors.BLUE}[*] Checking available models at: {Colors.END}{catalog_url}")
    print(f"{Colors.BLUE}[*] Using endpoint: {Colors.END}{datarobot_endpoint}")
    print()

    headers = {
        "Authorization": f"Bearer {datarobot_api_token}",
        "Content-Type": "application/json"
    }

    try:
        # Try without /api/v2 first
        response = requests.get(catalog_url, headers=headers)

        # If 404, try with /api/v2
        if response.status_code == 404:
            alt_url = f"{datarobot_endpoint}/genai/llmgw/catalog/"
            print(f"{Colors.YELLOW}[!] Got 404. Trying alternate endpoint: {Colors.END}{alt_url}")
            response = requests.get(alt_url, headers=headers)

        response.raise_for_status()
        catalog_data = response.json()

        # Handle different response formats
        if isinstance(catalog_data, list) and catalog_data:
            # Response is a direct list of models
            models = catalog_data
        elif isinstance(catalog_data, dict):
            if 'models' in catalog_data and catalog_data['models']:
                # Response has models in a 'models' key
                models = catalog_data['models']
            elif 'data' in catalog_data and catalog_data['data']:
                # Response has models in a 'data' key (paginated response)
                models = catalog_data['data']
            else:
                models = []
        else:
            models = []

        return models

    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}[X] Error fetching catalog: {e}{Colors.END}")
        print(f"{Colors.YELLOW}[i] Make sure your DATAROBOT_API_TOKEN and DATAROBOT_ENDPOINT are correct.{Colors.END}")
        print(f"{Colors.YELLOW}[i] If your endpoint includes /api/v2, both variants were tried. If errors persist, verify your account has LLM Gateway access and that the feature is enabled.{Colors.END}")
        sys.exit(1)

def display_models(models, provider_name=None):
    """Display models with optional provider filtering."""
    if not models:
        print(f"{Colors.YELLOW}[!] No models found{Colors.END}")
        return

    if provider_name and provider_name != "all":
        print_header(f"MODELS FROM {provider_name.upper()}")
        print(f"{Colors.BLUE}[i] Showing {len(models)} model(s) from {provider_name}{Colors.END}\n")
    else:
        print_header("AVAILABLE MODELS IN DATAROBOT CATALOG")

    for i, model in enumerate(models):
        print_model_info(model, i)

    print(f"{Colors.GREEN}[OK] Found {len(models)} model(s) in your catalog{Colors.END}")

def generate_html_report(models, output_file):
    """Generate HTML report for models."""
    print(f"{Colors.BLUE}[*] Generating HTML report...{Colors.END}")
    try:
        # Import and run the HTML generator
        from generate_model_catalog import enrich_model_data, generate_html
        from datetime import datetime
        
        enriched_models = [enrich_model_data(model) for model in models]
        html_content = generate_html(enriched_models)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"{Colors.GREEN}[OK] HTML report generated: {output_file}{Colors.END}")
        print(f"{Colors.BLUE}[i] Open the file in your browser to view the interactive catalog{Colors.END}")
    except ImportError:
        print(f"{Colors.YELLOW}[!] HTML generator not available. Skipping HTML report.{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}[X] Error generating HTML report: {e}{Colors.END}")

def main():
    """Main function with interactive provider selection."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Fetch models from catalog
    models = fetch_models_catalog(datarobot_api_token, datarobot_endpoint)
    
    if not models:
        print(f"{Colors.YELLOW}[!] No models found in the catalog{Colors.END}")
        return
    
    # Determine provider selection mode
    selected_provider = None
    
    if args.all:
        # Non-interactive mode: show all models
        selected_provider = "all"
        print(f"{Colors.BLUE}[i] Non-interactive mode: showing all models{Colors.END}\n")
    elif args.provider:
        # Non-interactive mode: specific provider
        selected_provider = args.provider
        print(f"{Colors.BLUE}[i] Non-interactive mode: showing models from {args.provider}{Colors.END}\n")
    else:
        # Interactive mode: let user choose provider
        providers = get_available_providers(models)
        
        if not providers:
            print(f"{Colors.YELLOW}[!] No providers found in the catalog{Colors.END}")
            return
        
        if len(providers) == 1:
            # Only one provider available, skip selection
            selected_provider = providers[0]
            print(f"{Colors.BLUE}[i] Only one provider available: {providers[0]}{Colors.END}\n")
        else:
            # Multiple providers, show selection menu
            display_provider_menu(providers)
            selected_provider = get_user_provider_choice(providers)
            print()
    
    # Filter models based on selection
    filtered_models = filter_models_by_provider(models, selected_provider)
    
    # Display models
    display_models(filtered_models, selected_provider)
    
    # Generate HTML report if requested
    if args.html or args.report:
        output_file = Path(__file__).parent / "model_catalog.html"
        generate_html_report(filtered_models, output_file)

if __name__ == "__main__":
    main()




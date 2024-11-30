"""Web search commands."""
from typing import Dict, Any
from . import Command
import requests
from utils.log import log

class WebSearchCommand(Command):
    """Command to perform web searches using Searx.
    
    This command allows you to search the web using a local Searx instance.
    It returns the top 5 most relevant results with titles, URLs, and snippets.
    
    Arguments:
        query (str): The search query to execute. Should be a specific and focused search term.
    
    Returns:
        Dict containing:
        - status: "success" or "error"
        - query: The original search query
        - results: List of up to 5 results, each with title, url, and snippet
    """
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("query"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "query": "The search query to execute. Should be a specific and focused search term."
        }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args["query"]
        if not query:
            return {"status": "error", "error": "No search query provided"}
        
        log(f"Performing web search for: {query}")
        
        try:
            # Local Searx instance endpoint
            searx_url = "http://localhost:8888/search"
            
            # Parameters for the search request
            params = {
                'q': query,
                'format': 'json',
                'categories': 'general',
                'language': 'en'
            }
            
            response = requests.get(searx_url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            # Format the results
            formatted_results = {
                "query": query,
                "results": [
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", "")
                    }
                    for result in results.get("results", [])[:5]  # Limit to top 5 results
                ]
            }
            
            return {"status": "success", **formatted_results}
            
        except requests.exceptions.ConnectionError:
            error = "Could not connect to local Searx instance. Make sure it's running on http://localhost:8888"
            log(error)
            return {"status": "error", "error": error}
        except requests.exceptions.Timeout:
            error = "Search request timed out"
            log(error)
            return {"status": "error", "error": error}
        except Exception as e:
            error = f"Search failed: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

# Register command
from .registry import CommandRegistry
CommandRegistry.register("web_search", WebSearchCommand)

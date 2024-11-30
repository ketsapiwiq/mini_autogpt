"""Implementation of core actions that the AI assistant can perform."""

import think.memory as memory
from utils.log import log
import requests
from typing import Dict, Any


def conversation_history(args=None):
    """Get the full conversation history.
    
    Returns:
        list: List of conversation entries
    """
    return memory.get_response_history()


def web_search(args: Dict[str, Any]) -> Dict[str, Any]:
    """Perform a web search using local Searx instance.
    
    Args:
        args (dict): Contains 'query' key with the search term
    
    Returns:
        dict: Search results containing titles, urls, and content snippets
    """
    query = args.get('query', '')
    if not query:
        return {"error": "No search query provided"}
    
    log(f"Performing web search for: {query}")
    
    try:
        # Local Searx instance endpoint
        searx_url = "http://localhost:8888/search"
        
        # Parameters for the search request
        params = {
            'q': query,
            'format': 'json',
            'categories': 'general',  # You can adjust categories as needed
            'language': 'en'
        }
        
        response = requests.get(searx_url, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        
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
        
        return formatted_results
        
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to local Searx instance. Make sure it's running on http://localhost:8888"}
    except requests.exceptions.Timeout:
        return {"error": "Search request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Search failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error during search: {str(e)}"}

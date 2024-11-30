"""Web search commands."""
from typing import Dict, Any, Optional
from . import Command
from .prompt_builder import BasicPromptTemplate
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
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get the prompt template for web search.
        
        The prompt helps the LLM understand how to process web search results.
        """
        template = """You are analyzing web search results for the query: {query}

Your task is to:
1. Extract key information from each result
2. Identify the most relevant information for the query
3. Note any conflicting information between sources
4. Consider the credibility of each source
5. Synthesize the findings into a coherent summary

Search Results:
{results}

Please provide:
1. A brief summary of the most relevant findings
2. Any important caveats or limitations
3. Suggestions for follow-up searches if needed
"""
        return BasicPromptTemplate(template)
    
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
            
            # Process results
            results = response.json()
            
            # Format results for prompt
            formatted_results = []
            for result in results.get('results', [])[:5]:
                formatted_results.append({
                    'title': result.get('title'),
                    'url': result.get('url'),
                    'snippet': result.get('content')
                })
            
            return {
                "status": "success",
                "query": query,
                "results": formatted_results,
                "prompt": self.get_formatted_prompt({
                    "query": query,
                    "results": "\n".join(f"[{r['title']}]({r['url']})\n{r['snippet']}\n" 
                                       for r in formatted_results)
                })
            }
            
        except requests.RequestException as e:
            log(f"Error performing web search: {str(e)}")
            return {
                "status": "error",
                "error": f"Search request failed: {str(e)}"
            }

# Register command
from .registry import CommandRegistry
CommandRegistry.register("web_search", WebSearchCommand)

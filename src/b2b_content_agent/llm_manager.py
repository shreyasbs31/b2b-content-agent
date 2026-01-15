"""LLM Manager with Multi-Provider Fallback Support

This module provides intelligent LLM provider management with automatic fallback.
When one provider fails (503 errors, rate limits, etc.), it automatically switches
to the next available provider.

Supported Providers (in priority order):
1. Groq - Fast, reliable, generous free tier (14,400 req/day)
2. Google Gemini - Good quality, free tier (50 req/day)
3. OpenAI - High quality, requires paid account
4. Anthropic Claude - High quality, requires paid account

Usage:
    manager = LLMManager()
    llm_flash = manager.get_llm("flash")  # Fast model
    llm_pro = manager.get_llm("pro")      # Smart model
"""

import os
import logging
from typing import Optional, List, Dict
from crewai import LLM

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages multiple LLM providers with automatic fallback."""
    
    # Model configurations for each provider
    PROVIDER_MODELS = {
        "groq": {
            "flash": "groq/llama-3.1-8b-instant",     # Fast, small model
            "pro": "groq/llama-3.1-70b-versatile",    # Reasoning, strategy
        },
        "gemini": {
            "flash": "gemini/gemini-2.5-flash-lite",               # 1000 RPD! Best option
            "pro": "gemini/gemini-2.5-pro",                        # 50 RPD (smart model)
            "flash-exp": "gemini/gemini-exp-1206",                 # Experimental
            "thinking": "gemini/gemini-2.0-flash-thinking-exp-1219",  # Thinking model
        },
        "openai": {
            "flash": "gpt-4o-mini",
            "pro": "gpt-4o",
        },
        "anthropic": {
            "flash": "claude-3-5-haiku-20241022",
            "pro": "claude-3-5-sonnet-20241022",
        },
    }
    
    # API key environment variable names
    API_KEY_VARS = {
        "groq": "GROQ_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    
    def __init__(self, fallback_order: Optional[List[str]] = None):
        """Initialize LLM Manager.
        
        Args:
            fallback_order: Custom provider priority order. 
                          Default: ["gemini", "groq", "openai", "anthropic"]
        """
        self.fallback_order = fallback_order or ["gemini", "groq", "openai", "anthropic"]
        self.available_providers = self._detect_available_providers()
        
        if not self.available_providers:
            logger.warning("⚠️  No LLM providers configured! Please add API keys to .env")
        else:
            logger.info(f"✅ Available LLM providers: {', '.join(self.available_providers)}")
    
    def _detect_available_providers(self) -> List[str]:
        """Detect which providers have API keys configured."""
        available = []
        for provider in self.fallback_order:
            api_key_var = self.API_KEY_VARS.get(provider)
            if api_key_var and os.getenv(api_key_var):
                available.append(provider)
                logger.debug(f"✓ {provider.upper()} API key found")
            else:
                logger.debug(f"✗ {provider.upper()} API key not found ({api_key_var})")
        return available
    
    def get_llm(
        self, 
        model_type: str = "flash", 
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> LLM:
        """Get an LLM with automatic fallback support.
        
        Args:
            model_type: "flash" (fast) or "pro" (smart/reasoning)
            temperature: Model temperature (0.0-1.0)
            max_retries: Max retries per provider before fallback
            
        Returns:
            LLM instance configured with fallback
            
        Raises:
            RuntimeError: If no providers are available
        """
        if not self.available_providers:
            raise RuntimeError(
                "No LLM providers configured! Add at least one API key to .env:\n"
                "  - GROQ_API_KEY (recommended, free)\n"
                "  - GOOGLE_API_KEY (Gemini)\n"
                "  - OPENAI_API_KEY\n"
                "  - ANTHROPIC_API_KEY"
            )
        
        # Get primary model based on fallback order
        primary_provider = self.available_providers[0]
        primary_model = self._get_model_name(primary_provider, model_type)
        
        logger.info(f"🤖 Using {primary_model} from {primary_provider.upper()}")
        if len(self.available_providers) > 1:
            others = [p.upper() for p in self.available_providers[1:]]
            logger.info(f"   Fallback providers available: {', '.join(others)}")
        
        # Return simple LLM - fallback handled by rate_limiter retry logic
        # LiteLLM's fallback feature doesn't work reliably with CrewAI
        return LLM(
            model=primary_model,
            temperature=temperature,
        )
    
    def _get_model_name(self, provider: str, model_type: str) -> str:
        """Get the model name for a provider and type."""
        models = self.PROVIDER_MODELS.get(provider, {})
        model = models.get(model_type)
        
        if not model:
            # Fallback to flash if pro not available
            model = models.get("flash", "groq/llama-3.3-70b-versatile")
            logger.warning(f"Model type '{model_type}' not found for {provider}, using {model}")
        
        return model
    
    def get_fallback_llm(
        self, 
        failed_provider: str,
        model_type: str = "flash",
        temperature: float = 0.7,
    ) -> Optional[LLM]:
        """Get a fallback LLM after a provider fails.
        
        Args:
            failed_provider: The provider that failed
            model_type: "flash" or "pro"
            temperature: Model temperature
            
        Returns:
            LLM instance for next available provider, or None if none available
        """
        # Find next provider in fallback order
        try:
            failed_index = self.available_providers.index(failed_provider)
            if failed_index + 1 < len(self.available_providers):
                next_provider = self.available_providers[failed_index + 1]
                next_model = self._get_model_name(next_provider, model_type)
                
                logger.warning(f"⚠️  {failed_provider.upper()} failed, falling back to {next_provider.upper()} ({next_model})")
                
                return LLM(
                    model=next_model,
                    temperature=temperature,
                    api_key=os.getenv(self.API_KEY_VARS[next_provider]),
                )
        except (ValueError, IndexError):
            pass
        
        logger.error(f"❌ No more fallback providers available after {failed_provider}")
        return None
    
    def get_provider_info(self) -> Dict[str, any]:
        """Get information about available providers."""
        return {
            "available_providers": self.available_providers,
            "fallback_order": self.fallback_order,
            "primary_provider": self.available_providers[0] if self.available_providers else None,
            "models": {
                provider: self.PROVIDER_MODELS.get(provider, {})
                for provider in self.available_providers
            }
        }
    
    def print_status(self):
        """Print current LLM provider status."""
        print("\n" + "="*80)
        print("🤖 LLM Provider Status")
        print("="*80)
        
        if not self.available_providers:
            print("❌ No providers configured!")
            print("\nTo fix this, add at least one API key to .env:")
            print("  GROQ_API_KEY=your_key_here      (Recommended - free & fast)")
            print("  GOOGLE_API_KEY=your_key_here    (Gemini)")
            print("  OPENAI_API_KEY=your_key_here    (GPT-4)")
            print("  ANTHROPIC_API_KEY=your_key_here (Claude)")
        else:
            print(f"✅ Primary Provider: {self.available_providers[0].upper()}")
            if len(self.available_providers) > 1:
                print(f"🔄 Fallback Providers: {', '.join(p.upper() for p in self.available_providers[1:])}")
            else:
                print("⚠️  No fallback providers (add more API keys for redundancy)")
            
            print("\nAvailable Models:")
            for provider in self.available_providers:
                models = self.PROVIDER_MODELS.get(provider, {})
                flash = models.get("flash", "N/A")
                pro = models.get("pro", "N/A")
                print(f"  {provider.upper():12} | Flash: {flash:40} | Pro: {pro}")
        
        print("="*80 + "\n")


# Global singleton instance
_llm_manager = None


def get_llm_manager(fallback_order: Optional[List[str]] = None) -> LLMManager:
    """Get the global LLM manager instance."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager(fallback_order)
    return _llm_manager


# Convenience functions
def get_flash_llm(temperature: float = 0.7) -> LLM:
    """Get a fast LLM (flash model)."""
    return get_llm_manager().get_llm("flash", temperature)


def get_pro_llm(temperature: float = 0.7) -> LLM:
    """Get a smart LLM (pro/reasoning model)."""
    return get_llm_manager().get_llm("pro", temperature)


def print_llm_status():
    """Print current LLM provider status."""
    get_llm_manager().print_status()


if __name__ == "__main__":
    # Test the manager
    print("\n🧪 Testing LLM Manager\n")
    manager = LLMManager()
    manager.print_status()
    
    if manager.available_providers:
        print("\nTesting LLM creation:")
        try:
            flash = manager.get_llm("flash")
            print(f"✅ Flash LLM: {flash.model}")
            
            pro = manager.get_llm("pro")
            print(f"✅ Pro LLM: {pro.model}")
        except Exception as e:
            print(f"❌ Error: {e}")

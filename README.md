# B2B Content Agent System

An AI-powered multi-agent system that automatically generates **100+ pieces of B2B marketing content** from a single product description. Built with CrewAI, featuring 10 specialized AI agents across 3 collaborative crews with human-in-the-loop quality control.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-1.3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

This system transforms a simple product description into a comprehensive B2B content library:

| Content Type | Quantity | Word Count             |
| ------------ | -------- | ---------------------- |
| Case Studies | 50       | 1,500-2,500 words each |
| White Papers | 25       | 3,000-5,000 words each |
| Pitch Decks  | 10       | 10-15 slides each      |
| Social Posts | 25       | Platform-optimized     |

**Total Output: 100+ pieces of content** tailored to different customer personas and use cases.

## Architecture

The system employs a **3-crew pipeline** with 10 specialized AI agents:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CREW 1: Research & Planning                  │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────┐     │
│  │  Product    │  │    Persona      │  │    Content       │     │
│  │  Analyst    │──│   Researcher    │──│   Strategist     │     │
│  └─────────────┘  └─────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CREW 2: Content Generation                    │
│  ┌────────────┐ ┌─────────────┐ ┌───────────┐ ┌──────────────┐  │
│  │Case Study  │ │White Paper  │ │Pitch Deck │ │Social Media  │  │
│  │  Writer    │ │   Author    │ │ Designer  │ │ Specialist   │  │
│  └────────────┘ └─────────────┘ └───────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CREW 3: Review & Polish                      │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────┐     │
│  │   Quality   │  │   Brand Voice   │  │      SEO         │     │
│  │  Assurance  │──│    Guardian     │──│   Optimizer      │     │
│  └─────────────┘  └─────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Crew       | Agent                   | Role                                                            |
| ---------- | ----------------------- | --------------------------------------------------------------- |
| **Crew 1** | Product Analyst         | Extract product features, benefits, and competitive positioning |
|            | Persona Researcher      | Identify 25 target customer personas with pain points           |
|            | Content Strategist      | Map content types to personas and create assignments            |
| **Crew 2** | Case Study Writer       | Create compelling customer success stories                      |
|            | White Paper Author      | Write authoritative thought leadership content                  |
|            | Pitch Deck Designer     | Structure persuasive executive presentations                    |
|            | Social Media Specialist | Craft platform-optimized social content                         |
| **Crew 3** | Quality Assurance       | Review accuracy, completeness, and quality                      |
|            | Brand Voice Guardian    | Ensure brand consistency across all content                     |
|            | SEO Optimizer           | Optimize for search visibility and readability                  |

## Key Features

- **Multi-Provider LLM Support**: Automatic failover between Groq, Gemini, OpenAI, and Claude
- **Human-in-the-Loop (HITL)**: 5 review checkpoints for human approval and feedback
- **Session Persistence**: Resume interrupted sessions without losing progress
- **Intelligent Rate Limiting**: Built-in quota management for API calls
- **Modular Architecture**: Each crew operates independently with clear interfaces

## Quick Start

### Prerequisites

- Python 3.11+
- At least one LLM API key (Groq, Gemini, OpenAI, or Anthropic)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/b2b-content-agent.git
cd b2b-content-agent

# Run the installer
./install.sh

# Or manual installation
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your API keys:

```env
# At least one is required
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Usage

1. **Edit `examples/input.txt`** with your product information:

```text
Product: Your Product Name

Description of your product, key features, target market,
pricing, and any other relevant information.
```

2. **Run the system:**

```bash
./run.sh
```

3. **Review outputs** in the `output/` directory:
   - `case_studies/` - Customer success stories
   - `white_papers/` - Thought leadership content
   - `pitch_decks/` - Executive presentations
   - `social_media/` - Platform-ready posts

## Project Structure

```
b2b-content-agent/
├── src/
│   └── b2b_content_agent/
│       ├── crew.py                     # Crew 1: Research & Planning
│       ├── content_generation_crew.py  # Crew 2: Content Generation
│       ├── review_polish_crew.py       # Crew 3: Review & Polish
│       ├── hitl_flow.py                # Human-in-the-loop orchestration
│       ├── llm_manager.py              # Multi-provider LLM management
│       ├── rate_limiter.py             # API rate limiting
│       ├── recovery.py                 # Session persistence & recovery
│       ├── config/                     # Agent & task YAML configurations
│       └── tools/                      # Custom tools for each agent
├── tests/                              # Test suite
├── examples/                           # Sample product inputs
├── output/                             # Generated content output
├── install.sh                          # Installation script
├── run.sh                              # Main execution script
└── requirements.txt
```

## Tech Stack

| Component          | Technology                   |
| ------------------ | ---------------------------- |
| Agent Framework    | CrewAI 1.3.0+                |
| LLM Providers      | Groq, Gemini, OpenAI, Claude |
| Language           | Python 3.11+                 |
| Configuration      | YAML                         |
| Package Management | pip, pyproject.toml          |

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_rate_limiter.py -v
```

## Performance

- **Average Runtime**: 15-30 minutes for full content generation
- **API Calls**: ~150-200 calls per full run
- **Cost**: ~$0.10-0.30 per run (varies by provider)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI)
- Multi-provider LLM support inspired by LangChain patterns

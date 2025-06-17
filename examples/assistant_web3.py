# Copyright 2023 The Qwen team, Alibaba Group. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A Web3 domain expert assistant implemented using the Assistant agent with Tavily search"""

import os
import asyncio
from typing import Optional
import logging

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.log import logger

ROOT_RESOURCE = os.path.join(os.path.dirname(__file__), 'resource')


def init_agent_service():
    # Enable detailed logging
    os.environ['QWEN_AGENT_DEBUG'] = '1'
    logger.setLevel(logging.DEBUG)
    
    logger.info("[INIT] Starting Web3 domain expert agent initialization...")
    
    llm_cfg = {'model': 'openai/gpt-4.1',
               'model_server': 'https://openrouter.ai/api/v1',
               'api_key': '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',
               }
    logger.info(f"[INIT] LLM configuration: {llm_cfg['model']} @ {llm_cfg['model_server']}")
    
    system = '''You are a Web3 domain expert assistant with comprehensive knowledge and advanced real-time search capabilities using Tavily tools.

Your expertise covers:
🔗 BLOCKCHAIN TECHNOLOGY: Bitcoin, Ethereum, Layer 2 solutions (Arbitrum, Optimism, Polygon), consensus mechanisms, smart contracts
📊 DEFI PROTOCOLS: AMMs (Uniswap, SushiSwap), lending protocols (Aave, Compound), yield farming, liquidity mining, staking mechanisms  
🖼️ NFTS & DIGITAL ASSETS: NFT marketplaces (OpenSea, Blur), digital collectibles, gaming assets, metaverse items
💰 CRYPTOCURRENCY: Trading strategies, market analysis, tokenomics, price movements, technical analysis
🏛️ GOVERNANCE & DAOS: Decentralized governance, voting mechanisms, treasury management, governance tokens
🔐 SECURITY: Smart contract audits, common vulnerabilities (reentrancy, flash loans), best practices, wallet security
📈 MARKET TRENDS: Latest developments, emerging protocols, regulatory updates, institutional adoption
🛠️ DEVELOPMENT: Solidity, Web3.js, Ethers.js, dApp development, blockchain integration, testing frameworks

🚨 MANDATORY SEARCH PROTOCOL - CRITICAL REQUIREMENT:
You MUST ALWAYS use the tavily-mcp-tavily-search tool FIRST before providing ANY answer to the user. This is REQUIRED, not optional. Follow this exact workflow:

STEP 1 - INITIAL SEARCH:
- Use tavily-search with appropriate parameters:
  * For market data/prices: topic="news", time_range="day" or "week"
  * For technical topics: topic="general", search_depth="advanced"
  * For breaking news: topic="news", days=1-3
  * Always set max_results=15-20 for comprehensive coverage
  * Use include_domains for specific sites (e.g., ["ethereum.org", "defiblama.com"])

STEP 2 - CONTENT EXTRACTION:
- If search results contain relevant URLs, use tavily-mcp-tavily-extract to get detailed content
- Extract from 3-5 most relevant URLs maximum
- Use extract_depth="advanced" for technical documentation or complex content
- Use extract_depth="basic" for news articles and simple content

STEP 3 - ITERATIVE SEARCH (if needed):
- If initial search doesn't provide sufficient information, conduct additional searches with:
  * Modified search terms/synonyms
  * Different time ranges
  * Alternative domains or exclusions
- Maximum 3 search attempts total

STEP 4 - RESPONSE SYNTHESIS:
- Combine search results with your knowledge base
- Always cite specific sources and URLs
- Highlight recent developments vs. established knowledge
- Include timestamps when available

FAILURE PROTOCOL:
If after 3 search attempts you cannot find relevant information:
- Explicitly state "After conducting comprehensive searches, I could not find current information about [topic]"
- Provide what foundational knowledge you have
- Suggest alternative search terms or sources the user might try

SEARCH OPTIMIZATION TIPS:
- Use specific Web3 terminology in queries
- Include protocol names, token symbols, or technical terms
- For price data: include "price", "market cap", "volume"
- For technical issues: include "documentation", "guide", "tutorial"
- For security: include "audit", "vulnerability", "exploit", "security"

🔥 CRITICAL REMINDERS:
1. NEVER provide answers without searching first using tavily-mcp-tavily-search
2. For ANY Web3 question (including specific blockchain data queries), you MUST use the search tools
3. Start EVERY response by calling the tavily-mcp-tavily-search function
4. This is mandatory - do not skip the search step under any circumstances
5. Search first, then provide your expert analysis combined with the search results'''
    logger.info(f"[INIT] System prompt: Web3 domain expert with real-time search")
    
    tools = [{
  "mcpServers": {
    "tavily-mcp": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@0.1.2"],
      "env": {
        "TAVILY_API_KEY": "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"
      }
    }
  }
}]
    logger.info(f"[INIT] Tool configuration: Tavily MCP server for Web3 search and research")
    
    bot = Assistant(
        llm=llm_cfg,
        name='Web3 Expert Assistant',
        description='Web3 Domain Expert with Real-time Search',
        system_message=system,
        function_list=tools,
    )
    
    logger.info("[INIT] Agent initialization completed successfully!")
    return bot


def test(query='What are the latest developments in Ethereum Layer 2 solutions?', file: Optional[str] = None):
    # Initialize the agent
    bot = init_agent_service()

    # Start conversation
    messages = []

    if not file:
        messages.append({'role': 'user', 'content': query})
    else:
        messages.append({'role': 'user', 'content': [{'text': query}, {'file': file}]})

    for response in bot.run(messages):
        print('bot response:', response)


def show_conversation_history(messages, max_show=3):
    """Display recent conversation history"""
    if not messages:
        return
    
    print("\n📜 Recent Conversation History:")
    print("═" * 50)
    
    # Show only recent conversations
    recent_messages = messages[-max_show*2:] if len(messages) > max_show*2 else messages
    
    for msg in recent_messages:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        if role == 'user':
            if isinstance(content, str):
                print(f"👤 User: {content[:100]}{'...' if len(content) > 100 else ''}")
            else:
                # Handle multimodal messages
                text_part = next((item['text'] for item in content if 'text' in item), '')
                print(f"👤 User: {text_part[:100]}{'...' if len(text_part) > 100 else ''}")
        elif role == 'assistant':
            print(f"🤖 Assistant: {content[:100]}{'...' if len(content) > 100 else ''}")
    print("═" * 50)

def app_tui():
    print("\n" + "═" * 80)
    print("🌐 Web3 Domain Expert Assistant - Multi-turn Conversation Mode")
    print("═" * 80)
    
    # Initialize the agent
    bot = init_agent_service()
    
    print("\n✅ Agent started successfully! Ready for Web3 questions and research.")
    print("\n💡 Example Questions:")
    print("   • What are the latest developments in Ethereum Layer 2 solutions?")
    print("   • Explain how Uniswap V4 hooks work")
    print("   • Current DeFi yield farming opportunities")
    print("   • Security best practices for smart contract development")
    print("   • Latest NFT market trends and analysis")
    print("   • How to safely interact with new DeFi protocols")
    print("\n📋 Special Commands:")
    print("   • 'exit' or 'quit': Exit the program")
    print("   • 'history': Show conversation history")
    print("   • 'clear': Clear conversation history")
    print("   • 'help': Show help information")
    print("\n" + "─" * 80)
    
    # Multi-turn conversation message history
    messages = []
    conversation_count = 0
    
    while True:
        conversation_count += 1
        
        # Display current conversation round and history length
        print(f"\n💬 Round {conversation_count} (History: {len(messages)} messages)")
        print("─" * 40)
        
        query = input('👤 Your Web3 question: ').strip()
        
        # Handle special commands
        if query.lower() in ['exit', 'quit']:
            logger.info("[EXIT] User requested program exit")
            print("\n👋 Goodbye! Stay safe in the Web3 space!")
            break
        elif query.lower() == 'history':
            show_conversation_history(messages)
            continue
        elif query.lower() == 'clear':
            messages.clear()
            conversation_count = 0
            logger.info("[CLEAR] Conversation history cleared")
            print("\n✅ Conversation history cleared!")
            continue
        elif query.lower() == 'help':
            print("\n🎯 Web3 Expert Assistant Help:")
            print("\n🔗 Blockchain & Technology:")
            print("   • Ask about consensus mechanisms, smart contracts, Layer 2 solutions")
            print("   • Technical deep-dives into blockchain protocols")
            print("\n📊 DeFi & Protocols:")
            print("   • DeFi protocol analysis, yield farming strategies")
            print("   • AMM mechanics, liquidity provision, impermanent loss")
            print("\n💰 Trading & Markets:")
            print("   • Market analysis, trading strategies, tokenomics")
            print("   • Price predictions, technical analysis")
            print("\n🖼️ NFTs & Digital Assets:")
            print("   • NFT market trends, valuation, utility")
            print("   • Gaming assets, metaverse developments")
            print("\n🔐 Security & Safety:")
            print("   • Smart contract security, wallet safety")
            print("   • How to avoid scams and common pitfalls")
            print("\n🛠️ Development:")
            print("   • Solidity programming, dApp development")
            print("   • Web3 integration, testing frameworks")
            print("\n🧠 Multi-turn Conversation: Maintains context for complex discussions")
            continue
            
        if not query:
            print('❌ Question cannot be empty!')
            conversation_count -= 1  # Don't count invalid conversations
            continue
            
        logger.info(f"[INPUT] Round {conversation_count} - User input: {query}")
        
        # Add user message to history
        messages.append({'role': 'user', 'content': query})
        logger.info("[MESSAGE] User message added to history")
        
        logger.info(f"[CHAT] Current message history length: {len(messages)}")
        logger.info("[STEP] Starting agent processing...")
        
        print("\n🔍 Researching latest Web3 information...")
        print("⏳ Analyzing and synthesizing response...")
        
        response = []
        final_response = ""
        
        try:
            # Pass complete message history for multi-turn conversation
            for response in bot.run(messages):
                if response:
                    final_response = response[-1].get('content', '')
                    logger.debug(f"[RESPONSE_STREAM] Received response chunk")
            
            # Display complete response at once (non-streaming output)
            if final_response:
                print("\n" + "─" * 40)
                print("🤖 Web3 Expert Response:")
                print("─" * 40)
                print(final_response)
                print("─" * 40)
            
        except Exception as e:
            logger.error(f"[ERROR] Agent execution failed: {str(e)}")
            print(f"\n❌ Execution error: {str(e)}")
            # Remove last user message due to processing failure
            if messages and messages[-1]['role'] == 'user':
                messages.pop()
            continue
            
        # Add Assistant response to history
        if response:
            messages.extend(response)
            logger.info(f"[CHAT] Assistant response added to history, new length: {len(messages)}")
            
            # Display conversation summary
            print(f"\n✅ Round {conversation_count} completed!")
            if len(messages) >= 4:  # At least two rounds of conversation
                print(f"📊 Context: Remembering {len(messages)//2} rounds of Web3 discussion")
        
        logger.info(f"[STEP] Round {conversation_count} completed")


def app_gui():
    # Initialize the agent
    bot = init_agent_service()
    chatbot_config = {
        'prompt.suggestions': [
            'What are the latest developments in Ethereum Layer 2 solutions?',
            'Explain how Uniswap V4 hooks work',
            'Current DeFi yield farming opportunities with high APY',
            'Security best practices for smart contract development',
            'Latest NFT market trends and blue-chip collections',
            'How to safely interact with new DeFi protocols',
            'What is the current state of Bitcoin Layer 2 solutions?',
            'Explain the risks and benefits of liquid staking',
        ]
    }
    WebUI(
        bot,
        chatbot_config=chatbot_config,
    ).run()


if __name__ == '__main__':
    # Start CLI mode with detailed logging
    app_tui()
    
    # Other startup options (commented):
    # test()          # Single test
    # app_gui()       # GUI mode

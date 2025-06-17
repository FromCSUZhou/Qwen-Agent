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

"""A SQLite database assistant implemented using the Assistant agent"""

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
    
    logger.info("[INIT] Starting database assistant agent initialization...")
    
    llm_cfg = {'model': 'openai/gpt-4.1',
               'model_server': 'https://openrouter.ai/api/v1',
               'api_key': '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',
               }
    logger.info(f"[INIT] LLM configuration: {llm_cfg['model']} @ {llm_cfg['model_server']}")
    
    system = ('You are a database assistant with the ability to query and manage SQLite databases')
    logger.info(f"[INIT] System prompt: {system}")
    
    tools = [{
        "mcpServers": {
            "sqlite" : {
                "command": "uvx",
                "args": [
                    "mcp-server-sqlite",
                    "--db-path",
                    "test.db"
                ]
            }
        }
    }]
    logger.info(f"[INIT] Tool configuration: SQLite MCP server, database path: test.db")
    
    bot = Assistant(
        llm=llm_cfg,
        name='Database Assistant',
        description='Database Query and Management',
        system_message=system,
        function_list=tools,
    )
    
    logger.info("[INIT] Agent initialization completed successfully!")
    return bot


def test(query='Show all tables in the database', file: Optional[str] = os.path.join(ROOT_RESOURCE, 'poem.pdf')):
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
    print("🗄️  SQLite Database Assistant - Multi-turn Conversation Mode")
    print("═" * 80)
    
    # Initialize the agent
    bot = init_agent_service()
    
    print("\n✅ Agent started successfully! Ready for multi-turn conversations.")
    print("\n💡 Example Questions:")
    print("   • Show all tables in the database")
    print("   • Create a students table with name and age columns")
    print("   • Insert a student named Alice, age 20")
    print("   • Query all student information")
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
        
        query = input('👤 Your question: ').strip()
        
        # Handle special commands
        if query.lower() in ['exit', 'quit']:
            logger.info("[EXIT] User requested program exit")
            print("\n👋 Goodbye! Thank you for using the Database Assistant!")
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
            print("\n🎯 Database Assistant Help:")
            print("\n📦 Supported Operations:")
            print("   • Query table structure: SELECT * FROM sqlite_master WHERE type='table';")
            print("   • Create table: CREATE TABLE table_name (column1 TYPE, column2 TYPE);")
            print("   • Insert data: INSERT INTO table_name (column1, column2) VALUES (value1, value2);")
            print("   • Query data: SELECT * FROM table_name;")
            print("   • Update data: UPDATE table_name SET column1=value1 WHERE condition;")
            print("   • Delete data: DELETE FROM table_name WHERE condition;")
            print("\n🧠 Multi-turn Conversation: Supports context memory, can reference previous operations")
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
        
        print("\n🤔 Agent is thinking... (based on full conversation history)")
        print("⏳ Processing your request...")
        
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
                print("🤖 Assistant Response:")
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
                print(f"📊 Context: Remembering {len(messages)//2} rounds of conversation")
        
        logger.info(f"[STEP] Round {conversation_count} completed")


def app_gui():
    # Initialize the agent
    bot = init_agent_service()
    chatbot_config = {
        'prompt.suggestions': [
            'Show all tables in the database',
            'Create a students table with name and age columns',
            'Insert a student named Alice, age 20',
            'Query all student information',
            'Delete the student named Alice',
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

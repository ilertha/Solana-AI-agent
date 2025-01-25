# Solana AI Agent

## Overview

### Why Choose Solana AI Agent?

#### Comprehensive Features
- **Built on CyberChipped**: A robust Python framework for OpenAI assistants.
- **Enhanced Capabilities**: Offers conversational memory, parallel function execution, smart tool selection, and message history with MongoDB.
- **Frameworks Utilized**: Leverages FastAPI and Next.js, two of the most popular web frameworks.
- **Customization Made Easy**: Quickly integrate custom functions into your AI agent with minimal code.
- **Key Actions**:
  - Transfer tokens from the Agent wallet to other wallets via Helius.
  - Swap tokens within the Agent wallet using Jupiter and Helius.
- **Social Media Integration**:
  - Connects to X through the X API (Basic Plan).

#### Superior to Eliza
- **No Code Changes Required**: Just add simple environment variables along with MongoDB/Redis for an out-of-the-box AI agent with real-time chat.
- **Advanced Conversational History**: Outperforms Retrieval-Augmented Generation (RAG) in user interaction, tool usage, and memory/context recall.
- **Efficient Tool Usage**: Offers parallel tool calling and automatic AI tool selection, surpassing any LLM completion API.
- **Simplicity in Design**: An opinionated framework with a straightforward approach to functionality.
- **Python-Based**: Developed in Python, the leading language in AI and GitHub projects.
- **Real-Time Responses**: Interacts on X in real-time, responding only when necessary.

## Local Development

### Running Locally on Mac or Linux
1. Clone the repository:
   ```bash
   git clone https://github.com/rizzolib/Solana-AI-agent
   ```
2. Ensure you have the latest LTS version of Node installed with Yarn.
3. Install Python 3.12.7 using Poetry.
4. Install Docker and Docker Compose.
5. Start the services:
   ```bash
   docker-compose up -d
   ```
6. Rename `.env.sample` to `.env` in both `site` and `agent` directories.
7. Set the `PRIVATE_KEY` (in base58 format) in the `.env` file within the `site` folder for Solana actions.
8. Obtain and set your `OPENAI_API_KEY` in the `agent` folder's `.env` file. [Get OpenAI API Keys](https://platform.openai.com/api-keys).
9. Set `HELIUS_API_KEY` and `HELIUS_RPC_URL` in both `.env` files. [Learn More About Helius](https://helius.dev).
10. For XBot integration, create an X developer account and configure the keys in the `agent` folder's `.env` file; uncomment the relevant code in `main.py`.
11. Ensure all secrets match between the `.env` files, using `uuidv4` or other secure keys.
12. Open two terminal windows:
    - **Terminal 1**: 
      ```bash
      cd site && yarn install && yarn dev
      ```
    - **Terminal 2**: 
      ```bash
      cd agent && poetry install && bash ./dev.sh
      ```
13. Access the application in your browser at `http://localhost:3000`.

## Deployment

### Deploying to Heroku or Dokku
1. Provision MongoDB and Redis databases.
2. Acquire a domain with two subdomains for the `site` and `agent`.
3. Configure the necessary environment variables on Heroku or Dokku.
4. Initialize Git repositories for both `site` and `agent` folders.
5. Commit and push changes to the main branch for both folders.
6. Scale the worker and scheduler to 1 (the web should already be set to 1).

## Advanced Topics

### Agent Functions
- Use clear snake-case naming for functions and descriptive parameter names.
- Functions should accept only `str` parameters and return a `str`.
- Ensure functions are synchronous; avoid async libraries or methods (e.g., use `requests` instead of `httpx`).
- Limit the size of tool outputs (strings) to accommodate multiple parallel calls within size limits.
- Consider the 128k token input limit when processing data, especially from APIs.
- Opt for OpenAI `gpt-4o` for better performance over `gpt-4o-mini`, unless cost is a concern.

## Production Applications
- [WB AI Agent](https://ai.walletbubbles.com)
- [Solana Agent X Bot](https://solana-agent.com)

"""
GLIMMER Web CLI - Command line interface for GLIMMER Agent.
"""

import argparse
from glimmer_web import GlimmerAgent, AgentConfig
from glimmer_web.model.client import ModelConfig


def main():
    parser = argparse.ArgumentParser(description="GLIMMER GUI Automation Agent")
    parser.add_argument("goal", nargs="?", help="Task goal to accomplish")
    parser.add_argument("--model-url", default="http://localhost:8000/v1", help="Model API URL")
    parser.add_argument("--model-name", default="glm-4v", help="Model name")
    parser.add_argument("--api-key", default="EMPTY", help="API key")
    parser.add_argument("--lang", default="en", choices=["en", "cn"], help="Language")
    parser.add_argument("--max-steps", type=int, default=50, help="Maximum steps")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    model_config = ModelConfig(
        base_url=args.model_url,
        model_name=args.model_name,
        api_key=args.api_key,
        lang=args.lang,
    )
    
    agent_config = AgentConfig(
        max_steps=args.max_steps,
        lang=args.lang,
    )
    
    agent = GlimmerAgent(model_config, agent_config)
    
    if args.interactive:
        print("🤖 GLIMMER Interactive Mode")
        print("Type 'quit' to exit, 'reset' to start new task")
        print("-" * 50)
        
        while True:
            goal = input("\n📝 Enter goal: ").strip()
            if goal.lower() == "quit":
                break
            elif goal.lower() == "reset":
                agent.reset()
                print("✅ Agent reset")
                continue
            elif not goal:
                continue
            
            agent.run(goal)
    else:
        if not args.goal:
            parser.print_help()
            return
        agent.run(args.goal)


if __name__ == "__main__":
    main()

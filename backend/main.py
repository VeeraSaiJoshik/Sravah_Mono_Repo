#PM Automation Agent - Main Entry Point
from utils.conversation_state import ConversationState
from agents.orchestrator import run_orchestrator_turn
from database.mongo_client import close_connection
import sys

def print_separator():
    print("\n" + "="*70 + "\n")


def print_welcome():
    print("SRAVAH")
    print("="*70)
    print("\nJust tell me what you're working on or any blockers you're facing,")
    print("and I'll figure out which project you mean!")
    print("\nType 'quit' to exit.")
    print_separator()


def main():
    print_welcome()
    
    #conversation state init
    state = ConversationState()
    print("SRAVAH: Hi! What are you working on today? Any updates or blockers?")
    print_separator()
    
    # Main loop
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break    
            if not user_input:
                continue 
            print_separator()
            
            # Process with orchestrator
            response, project_identified = run_orchestrator_turn(state, user_input)
            print(f"\nSRAVAH: {response}")
            
            # Show state summary
            print(f"\nStatus: {state.get_summary()}")
            print_separator()
            
            # Optional: Exit after project identified
            if project_identified and state.identified_project_id:
                follow_up = input("\n❓ Would you like to continue the conversation? (y/n): ").strip().lower()
                if follow_up != 'y':
                    print("\n✅ Great! I've identified your project. Goodbye!")
                    break
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            
            # Ask if user wants to continue
            continue_choice = input("\nWould you like to continue? (y/n): ").strip().lower()
            if continue_choice != 'y':
                break
    
    # Cleanup
    close_connection()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
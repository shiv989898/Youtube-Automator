import subprocess
import sys
from datetime import datetime

def main():
    """
    Determines which video generation script to run based on the current hour.
    - Even hours: Runs the YouTube Shorts script (main.py).
    - Odd hours:  Runs the Long-Form video script (main_long.py).
    """
    try:
        hour = datetime.now().hour
        
        if hour % 2 == 0:
            print(f"It is hour {hour} (even). Dispatching to YouTube Shorts generator.")
            script_to_run = 'main.py'
        else:
            print(f"It is hour {hour} (odd). Dispatching to Long-Form video generator.")
            script_to_run = 'main_long.py'
            
        print(f"Executing: python {script_to_run}")
        
        # Execute the chosen script, ensuring output is streamed to the console
        # and that the process uses the same Python interpreter.
        process = subprocess.run(
            [sys.executable, script_to_run],
            check=True,
            capture_output=False, # Allows real-time output
            text=True
        )
        
        print(f"Successfully executed {script_to_run}.")

    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_to_run}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred in the dispatcher: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

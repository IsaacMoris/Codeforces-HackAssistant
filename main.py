import subprocess as sub
import os
import sys
import shutil
import threading
import time
import argparse
import atexit

# --- Global Variables ---
# Configuration (will be set by args)
source_code_content = ""
compare_code_content = ""
generator_or_testcase_content = "" # Content of the generator or single test case
num_threads = 1
use_single_testcase_mode = False

# State
continue_executing = True # Flag to signal threads to stop
error_occurred = False    # Flag to indicate if an error stopped execution
final_error_message = ""  # Stores the first critical error message
test_num = 1              # Counter for passed tests
workers = []              # List of thread objects

# Locks
output_lock = threading.Lock()        # For thread-safe console printing
test_num_mutex = threading.Lock()     # For thread-safe access to test_num
setup_lock = threading.Lock()         # For serializing per-thread setup (compilation, generator.py writing)
error_message_lock = threading.Lock() # For thread-safe access to final_error_message and continue_executing

# --- Directory Setup ---
BASE_DIR = os.getcwd()
USABLE_DIR = os.path.join(BASE_DIR, "usable") # Directory for temporary files and executables

def setup_usable_dir():
    """Creates the 'usable' directory if it doesn't exist."""
    if not os.path.exists(USABLE_DIR):
        os.makedirs(USABLE_DIR)
        console_print(f"Created directory: {USABLE_DIR}")

def cleanup_usable_dir():
    """Removes the 'usable' directory. Registered with atexit to run on script exit."""
    if os.path.exists(USABLE_DIR):
        console_print(f"Cleaning up '{USABLE_DIR}' directory...")
        try:
            shutil.rmtree(USABLE_DIR)
            console_print(f"'{USABLE_DIR}' directory removed.")
        except Exception as e:
            console_print(f"Error removing '{USABLE_DIR}' directory: {e}", error=True)

atexit.register(cleanup_usable_dir) # Ensure cleanup happens on exit

# --- Helper Functions ---
def console_print(message, end="\n", error=False):
    """Prints messages atomically to the console (stdout or stderr)."""
    with output_lock:
        stream = sys.stderr if error else sys.stdout
        print(message, end=end, file=stream)
        stream.flush()

def rewrite(file_path, data):
    """Writes data to a file. Signals exit on failure."""
    try:
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(data)
    except IOError as e:
        signal_exit(f"FATAL: Failed to write to file {file_path}: {e}")


def signal_exit(reason_message):
    """
    Signals all threads to stop execution and records the primary error reason.
    Ensures that the primary reason is captured and printed only once.
    """
    global continue_executing, error_occurred, final_error_message
    
    first_to_signal = False
    with error_message_lock:
        if continue_executing: # If this is the first signal to stop
            continue_executing = False
            error_occurred = True
            if not final_error_message: # Store the first critical error message
                final_error_message = reason_message
            first_to_signal = True

    if first_to_signal:
        console_print(f"EXIT SIGNALED: {reason_message}", error=True)

def passed():
    """Increments and prints the count of passed test cases."""
    global test_num
    with test_num_mutex:
        console_print(f"Test Passed: {test_num}")
        test_num += 1

def execut(executable_name_no_ext, input_data_str, exec_type, thread_id_str=""):
    """
    Executes a C++ program or a Python script.
    - executable_name_no_ext: Name of the executable/script without extension (e.g., "source0", "generator0").
    - input_data_str: String data to be fed as input (for C++ via temp file, for Python via stdin if needed).
    - exec_type: "C" or "Python".
    - thread_id_str: Thread identifier (e.g., "0", "1") for unique input file naming for C++ programs.
    Returns (stdout_str, stderr_str).
    """
    cmd_list_or_str = None
    process_input_bytes = None
    shell_mode = False 
    exec_cwd = USABLE_DIR

    full_stdout = ""
    full_stderr = ""

    try:
        if exec_type == "Python":
            script_path = f'{executable_name_no_ext}.py'
            cmd_list_or_str = [sys.executable, script_path] # Use system's Python interpreter
            if input_data_str: # Pass input via stdin if provided
                 process_input_bytes = str(input_data_str).encode('utf-8', 'ignore')

        elif exec_type == "C":
            input_file_name = f"input{thread_id_str}.txt"
            # rewrite function expects full path
            rewrite(os.path.join(USABLE_DIR, input_file_name), str(input_data_str))
            
            # Command for C++: ./executable < input_file
            # Using shell=True here for the I/O redirection (<).
            # Ensure executable_name_no_ext and input_file_name are safe.
            cmd_list_or_str = f'./{executable_name_no_ext} < {input_file_name}'
            shell_mode = True
        else:
            return "", f"Unknown execution type: {exec_type}"

        p = sub.Popen(cmd_list_or_str,
                      stdout=sub.PIPE,
                      stderr=sub.PIPE,
                      stdin=sub.PIPE if process_input_bytes and exec_type == "Python" else None,
                      shell=shell_mode,
                      cwd=exec_cwd) # Execute from the 'usable' directory
        
        # Communicate with the process
        output_bytes, errors_bytes = p.communicate(input=process_input_bytes, timeout=15) # 15-second timeout

        full_stdout = output_bytes.decode('utf-8', errors='ignore').strip()
        full_stderr = errors_bytes.decode('utf-8', errors='ignore').strip()

        # If process exited with an error code but no stderr, provide basic error info
        if p.returncode != 0 and not full_stderr:
            full_stderr = f"Process exited with error code {p.returncode}"

    except sub.TimeoutExpired:
        p.kill() # Terminate the process if it times out
        output_bytes, errors_bytes = p.communicate() # Try to get any remaining output
        full_stdout = output_bytes.decode('utf-8', errors='ignore').strip()
        err_msg = errors_bytes.decode('utf-8', errors='ignore').strip()
        full_stderr = f"Timeout Error after 15s. Last stderr: {err_msg}".strip()
    except FileNotFoundError:
        exec_name = cmd_list_or_str[0] if isinstance(cmd_list_or_str, list) else executable_name_no_ext
        full_stderr = f"Execution Error: File or command not found - '{exec_name}' (cwd: {exec_cwd})"
    except Exception as e:
        full_stderr = f"Subprocess execution critical failure: {e}"

    return full_stdout, full_stderr

# --- Core Logic ---
def compares(input_text, thread_id_str):
    """
    Compares the output of two C++ solutions for a given input.
    Signals exit if outputs mismatch or if a runtime error occurs.
    Returns True if outputs match and no errors, False otherwise.
    """
    if not continue_executing: return False

    # Execute user's solution
    source_output, source_errors = execut(f"source{thread_id_str}", input_text, "C", thread_id_str)
    if not continue_executing: return False 
    if source_errors:
        signal_exit(f"Thread {thread_id_str}: Runtime Error on Your Solution!\nInput:\n{input_text}\nError:\n{source_errors}")
        return False

    # Execute solution to hack
    compare_output, compare_errors = execut(f"compare{thread_id_str}", input_text, "C", thread_id_str)
    if not continue_executing: return False
    if compare_errors:
        signal_exit(f"Thread {thread_id_str}: Runtime Error on Solution to Hack!\nInput:\n{input_text}\nError:\n{compare_errors}")
        return False

    # Compare outputs
    if source_output != compare_output:
        max_len = 200 # Truncate long outputs in error messages
        source_disp = source_output[:max_len] + ("..." if len(source_output) > max_len else "")
        compare_disp = compare_output[:max_len] + ("..." if len(compare_output) > max_len else "")
        signal_exit(f"Thread {thread_id_str}: Output Mismatch!\nInput:\n{input_text}\nYour Output:\n{source_disp}\nHack Output:\n{compare_disp}")
        return False
    
    return True


def run_test_loop(thread_id_str, single_mode, local_generator_content):
    """
    Main loop for a worker thread. Compiles codes, generates/uses test cases, and compares solutions.
    - thread_id_str: String identifier for the thread (e.g., "0").
    - single_mode: Boolean, True if using a single test case, False if generating.
    - local_generator_content: The Python generator code or the single test case data.
    """
    global continue_executing 
    
    thread_name = f"Thread-{thread_id_str}"
    console_print(f"{thread_name}: Starting up.")

    # --- Per-thread Setup (Compilation, Generator Script) ---
    with setup_lock: # Serialize setup to prevent g++ or file system race conditions
        if not continue_executing:
            console_print(f"{thread_name}: Halting before setup as exit is signaled.", error=True)
            return

        console_print(f"{thread_name}: Compiling C++ codes...")
        # Compile user's solution (source.cpp must be in USABLE_DIR)
        # Using common g++ flags: -std=c++17, -O2 (optimization), -pipe (may speed up compilation)
        cmd_source = ['g++', 'source.cpp', '-o', f'source{thread_id_str}', '-std=c++17', '-O2', '-pipe', '-DONLINE_JUDGE']
        p_source = sub.Popen(cmd_source, stdout=sub.PIPE, stderr=sub.PIPE, cwd=USABLE_DIR)
        _, errors_s_bytes = p_source.communicate()
        if p_source.returncode != 0:
            errors_s = errors_s_bytes.decode('utf-8', errors='ignore').strip()
            signal_exit(f"{thread_name}: Source Compilation Error!\n{errors_s}")
            return

        # Compile solution to hack (compare.cpp must be in USABLE_DIR)
        cmd_compare = ['g++', 'compare.cpp', '-o', f'compare{thread_id_str}', '-std=c++17', '-O2', '-pipe', '-DONLINE_JUDGE']
        p_compare = sub.Popen(cmd_compare, stdout=sub.PIPE, stderr=sub.PIPE, cwd=USABLE_DIR)
        _, errors_c_bytes = p_compare.communicate()
        if p_compare.returncode != 0:
            errors_c = errors_c_bytes.decode('utf-8', errors='ignore').strip()
            signal_exit(f"{thread_name}: Solution to Hack Compilation Error!\n{errors_c}")
            return
        console_print(f"{thread_name}: Compilation successful.")

        if not single_mode: # If generating test cases, write the generator script for this thread
            rewrite(os.path.join(USABLE_DIR, f"generator{thread_id_str}.py"), local_generator_content)
            console_print(f"{thread_name}: Generator script 'generator{thread_id_str}.py' prepared.")
    # --- End of locked setup ---

    test_count_this_thread = 0
    while continue_executing:
        current_test_input = ""
        if single_mode:
            if test_count_this_thread > 0: # Single mode runs only once per thread
                 break 
            current_test_input = local_generator_content # The content is the test case itself
            console_print(f"{thread_name}: Running single provided test case.")
        else:
            # Execute Python generator to get a test case
            gen_out, gen_err = execut(f'generator{thread_id_str}', "", "Python", thread_id_str)
            
            if not continue_executing: break # Check flag after potentially long generator execution

            if gen_err:
                signal_exit(f"{thread_name}: Generator Error!\n{gen_err}")
                return 
            
            current_test_input = gen_out 
            if not current_test_input: # If generator produces empty output
                console_print(f"{thread_name}: Generator produced empty input. Retrying...", error=True)
                time.sleep(0.2) 
                continue 
        
        # Compare outputs for the current_test_input
        match_result = compares(current_test_input, thread_id_str)
        
        if not continue_executing: break # Check if 'compares' signaled an exit

        if match_result:
            passed() 
        else:
            # 'compares' already called 'signal_exit'. Loop condition will handle termination.
            return 

        test_count_this_thread += 1
        if single_mode: # If in single_mode, break after the first test attempt
            console_print(f"{thread_name}: Single test case processed.")
            break 
        
        if not continue_executing and not single_mode: # Graceful exit if signaled
             console_print(f"{thread_name}: Stop signal received, winding down.")
             break
    
    console_print(f"{thread_name}: Finished work after {test_count_this_thread} tests.")


# --- Main Execution ---
def main():
    global source_code_content, compare_code_content, generator_or_testcase_content
    global num_threads, use_single_testcase_mode
    global workers 

    parser = argparse.ArgumentParser(
        description="Codeforces Hack Assistant (CLI) - Tests a solution against another using generated or provided test cases.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("source_file", help="Path to Your Solution C++ file (e.g., my_solution.cpp)")
    parser.add_argument("compare_file", help="Path to Solution to Hack C++ file (e.g., target_solution.cpp)")
    parser.add_argument("generator_file", help="Path to Test Case Generator Python file OR a file containing a single test case.")
    parser.add_argument("--threads", "-t", type=int, default=4, help="Number of threads for generating and testing (default: 4).\nUsed only if not in single testcase mode.")
    parser.add_argument("--single-testcase", "-s", action="store_true", help="Treat generator_file as a single test case input instead of a Python generator script.")
    
    args = parser.parse_args()

    num_threads_arg = args.threads
    use_single_testcase_mode = args.single_testcase

    if use_single_testcase_mode:
        num_threads = 1 # Single test case mode uses only one effective thread.
        console_print(f"Mode: Single Test Case. Effective threads: {num_threads}")
    else:
        num_threads = num_threads_arg
        console_print(f"Mode: Test Case Generation. Threads: {num_threads}")

    try:
        with open(args.source_file, 'r', encoding='utf-8') as f: source_code_content = f.read()
        with open(args.compare_file, 'r', encoding='utf-8') as f: compare_code_content = f.read()
        with open(args.generator_file, 'r', encoding='utf-8') as f: generator_or_testcase_content = f.read()
    except IOError as e:
        console_print(f"FATAL: Error reading input files: {e}", error=True)
        sys.exit(1)

    setup_usable_dir() # Create ./usable if it doesn't exist

    # Write the main C++ codes into the usable directory
    rewrite(os.path.join(USABLE_DIR, "source.cpp"), source_code_content)
    rewrite(os.path.join(USABLE_DIR, "compare.cpp"), compare_code_content)
    if not continue_executing: # Check if rewrite signaled an exit (e.g., directory not writable)
        console_print("FATAL: Failed to write initial C++ files into 'usable' directory. Exiting.", error=True)
        sys.exit(1)

    console_print("Starting worker threads...")
    for i in range(num_threads):
        thread_id_str = str(i)
        p = threading.Thread(target=run_test_loop, 
                             args=(thread_id_str, use_single_testcase_mode, generator_or_testcase_content), 
                             name=f"Tester-{i}")
        workers.append(p)
        p.start()
        console_print(f"Started Thread: {i} (ID: {thread_id_str})")
    
    if not workers:
        console_print("FATAL: No worker threads were started. Please check parameters.", error=True)
        sys.exit(1)

    try:
        # Keep main thread alive while workers run, allowing for KeyboardInterrupt
        while any(t.is_alive() for t in workers):
            time.sleep(0.5) 
            # If continue_executing becomes false due to a non-error signal (not currently implemented, but for future):
            if not continue_executing and not error_occurred:
                console_print("Main loop: continue_executing is false, but no specific error reported. Waiting for threads to finish.")
                break 
    except KeyboardInterrupt:
        console_print("\nKeyboardInterrupt received by main thread. Signaling threads to stop...", error=True)
        signal_exit("Execution aborted by user (Ctrl+C).")

    console_print("Waiting for all worker threads to complete...")
    for i, worker_thread in enumerate(workers):
        worker_thread.join(timeout=10) # Wait for each thread to finish with a timeout
        if worker_thread.is_alive():
            console_print(f"Warning: Thread {i} ({worker_thread.name}) did not exit cleanly after 10s timeout.", error=True)

    console_print("All threads have been processed.")
    if error_occurred:
        console_print(f"Execution FAILED. Reason: {final_error_message}", error=True)
        sys.exit(1) # Exit with error code
    else:
        console_print("Execution finished successfully. All run tests passed or no discrepancies found.")
        sys.exit(0) # Exit successfully

if __name__ == "__main__":
    main()
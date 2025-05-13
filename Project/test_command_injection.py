import command_injection

test_cases = [
    "hello && echo 'Injected'",         # Command chaining
    "test; echo 'injected'",            # Semicolon separation
    "$(echo injected)",                 # Subshell
    "`echo injected`",                  # Backticks (subshell)
    "normal message",                   # Safe input
    "echo Hello",	                    # Echo
    "try | echo test",                  # Pipe with command
]

def run_tests():
    print("Command Injection Test Results:")
    for i, input_text in enumerate(test_cases):
        try:
            print(f"\n🔹 Test {i+1}: Input: {repr(input_text)}")
            output = command_injection.process_peer_message(input_text)
            print("Resulting Output:", output)
        except Exception as e:
            print("Error occurred:", e)

if __name__ == "__main__":
    run_tests()




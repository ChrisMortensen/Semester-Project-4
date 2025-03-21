import time

def is_rate_limited(message_timestamps, MAX_MESSAGES_PER_SECOND):
    """
    Checks if the peer has exceeded the allowed message rate.

    Args:
        message_timestamps (deque): A deque storing timestamps of recent messages.
        MAX_MESSAGES_PER_SECOND (int): Maximum amout of messages per second.

    Returns:
        bool: True if the message should be dropped, False otherwise.
    """
    current_time = time.time()

    # Remove old timestamps older than 1 second
    while message_timestamps and message_timestamps[0] < current_time - 1:
        message_timestamps.popleft()

    if len(message_timestamps) >= MAX_MESSAGES_PER_SECOND:
        print(f"Rate limit exceeded for peer, dropping packet.")
        return True  # Drop the message

    message_timestamps.append(current_time)  # Store new timestamp
    return False  # Allow message
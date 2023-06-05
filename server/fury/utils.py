import time


def exponential_backoff(foo, *args, **kwargs):
    max_retries = 5  # Maximum number of retries
    retry_delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            out = foo(*args, **kwargs)  # Call the function that may crash
            return out  # If successful, break out of the loop and return
        except Exception as e:
            print(f"Function crashed: {e}")
            if attempt == max_retries - 1:
                print("Max retries reached. Exiting...")
                break
            else:
                delay = retry_delay * (2**attempt)  # Calculate the backoff delay
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)  # Wait for the calculated delay

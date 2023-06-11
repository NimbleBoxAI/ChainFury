import time


def exponential_backoff(foo, *args, max_retries=2, retry_delay=1, **kwargs):
    # Maximum number of retries
    # Initial delay in seconds

    errors = []
    for attempt in range(max_retries):
        try:
            out = foo(*args, **kwargs)  # Call the function that may crash
            return out  # If successful, break out of the loop and return
        except Exception as e:
            print(f"Function crashed: {e}")
            if attempt == max_retries - 1:
                print("Max retries reached. Exiting...")
                raise e
            else:
                delay = retry_delay * (2**attempt)  # Calculate the backoff delay
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)  # Wait for the calculated delay

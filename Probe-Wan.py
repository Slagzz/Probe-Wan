#!/usr/bin/env python3

import asyncio
import aiohttp
import time
import sys

# Timeout for HTTP requests (seconds)
timeout = 5

# Max number of concurrent connections
concurrency_limit = 100

async def check_domain(session, url):
    """Check if a URL is alive by sending an HTTP GET request."""
    try:
        async with session.get(url, timeout=timeout) as response:
            if response.status in [200, 403]:
                print(f"{url} (status {response.status})")
                return url  # Return alive URL
    except Exception as e:
        return None  # Ignore exceptions and return None if not successful

async def probe_domains(domains):
    """Probe a list of domains for aliveness."""
    alive_domains = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for domain in domains:
            task = asyncio.ensure_future(check_domain(session, domain))
            tasks.append(task)
        
        alive_results = await asyncio.gather(*tasks)
        alive_domains = [domain for domain in alive_results if domain is not None]
    
    return alive_domains

def read_domains_from_file(file_path):
    """Read a list of domains from a file."""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def write_alive_domains_to_file(file_path, alive_domains):
    """Write alive domains to a file."""
    with open(file_path, 'w') as f:
        for domain in alive_domains:
            f.write(f"{domain}\n")

async def main(input_file):
    domains = read_domains_from_file(input_file)
    start_time = time.time()

    print(f"Probing {len(domains)} domains...")
    alive_domains = await probe_domains(domains)
    
    print(f"Alive domains: {len(alive_domains)}")
    write_alive_domains_to_file('alive_domains.txt', alive_domains)
    
    print(f"Finished in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]

    # Set up asyncio concurrency limit
    loop = asyncio.get_event_loop()
    semaphore = asyncio.Semaphore(concurrency_limit)
    
    # Run the main function
    loop.run_until_complete(main(input_file))

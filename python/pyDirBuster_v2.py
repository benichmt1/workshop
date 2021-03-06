#!/usr/bin/python3
# Author: Jeremy Schoeneman (y4utj4)
# Thanks to: Coldfusion39 for the help!!
""" 
pyDirBuster is a python version of DirBuster which brute-forces and enumerates directories within a website. 
You'll need your own directory wordlist. 
"""

import aiohttp
import argparse
import asyncio
import signal

@asyncio.coroutine
def get_status(site, verbose, outfile, sem):
	
	with (yield from sem):
		response = yield from aiohttp.request('GET', site, compress=True)

	if response.status == 200: # Site Reached
		if verbose:
			print("[+] FOUND: {0}: {1}".format(site, response.status))
		if outfile:
			outfile.write("{0}: {1}".format(site, response.status) + '\n')
	elif 300 < response.status < 308: # Web Redirects
		if verbose:
			print("[!] Web Redirect: {0}: {1}".format(site, response.status))	
		if outfile:
			outfile.write("{0}: {1}".format(site, response.status) + '\n')
	elif response.status == 401: # Authorization Required
		if verbose:
			print("[!] Authorization Required: {0}: {1}".format(site, response.status))
		if outfile:
			outfile.write("{0}: {1}".format(site, response.status) + '\n')
	elif response.status == 403: # Forbidden
		if verbose:
			print("[!] Forbidden: {0}: {1}".format(site, response.status))
	elif response.status == 404: # Website not found
		if verbose:
			print("[-] Not Found: {0}: {1}".format(site, response.status))
	elif response.status == 503: # Service Unavailable
		if verbose:
			print("[-] Service Unavailable: {0}: {1}".format(site, response.status))
	else:
		if verbose: #catch all. Look up the status number
			print("[?] Unknown Response: {0}: {1}".format(site, response.status))
	
	yield from response.release()

def signal_handler():
	# cleans up
	print('Stopping all tasks')
	for task in asyncio.Task.all_tasks():
		task.cancel()

def main():
	# setup arguments
	parser = argparse.ArgumentParser(description='Put description here')
	parser.add_argument('-u', '--url', help='URL to look up')
	parser.add_argument('-w', '--wordlist', help='directory listing')
	parser.add_argument('-o', '--outfile', help='file to write output')
	parser.add_argument('-v', '--verbose', help='prints results to screen', action='store_true')

	# Assigning args
	args = parser.parse_args()
	outfile = 0
	if args.outfile:
		outfile = open(args.outfile, 'w')
	url = args.url
	verbose = args.verbose
	directories = open(args.wordlist, 'r')

	#limits the amount of concurrent open sockets to the server you can change the 1000
	sem = asyncio.Semaphore(1000)

	# Assigning loop and connection
	loop = asyncio.get_event_loop()
	loop.add_signal_handler(signal.SIGINT, signal_handler)

	# Do the things
	f = asyncio.wait([get_status(url + directory.rstrip('\n'), verbose, outfile, sem) for directory in directories])
	try:
		
		loop.run_until_complete(f)
	except asyncio.CancelledError:
		print('Tasks were canceled')

if __name__ == '__main__':
	main()

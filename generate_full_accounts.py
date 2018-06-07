import requests
import json
import numpy as np
import csv
import urllib.request as url
import urllib.error as urlerror
import time
import random
import socket

my_key = 'Put your Etherscan api key here'
num_api_requests = 0
num_found = 0
already_called = []


def main():
	global my_key
	top_ten_thousand_addrs = fillTopTenThousand()
	full_address_set = getAllAddresses(top_ten_thousand_addrs)

# Need to start recursive search
# Here I am using a CSV that I have with the top 10,000 ethereum address
# I read the CSV into a list that I then use to recursively find more addresses
# based on publicly available transaction history data
def fillTopTenThousand():
	result = []
	with open("accounts.csv", 'rt') as accountsCSV:
		accountReader = csv.reader(accountsCSV)
		counter = 0
		for account in accountReader:
			if counter is 0:
				counter = counter + 1
				continue
			result.append(account[1])
	return result


def recursive_search(result, top_ten_thousand_addrs, address, CSVwriter, recursive_level):
	global num_api_requests
	global num_found
	global already_called

	append_addr = True
	# If we've seen this address before then don't append it to result
	# If we're here then note that we have not yet recursively checked this address
	if (address in result or address is None):
		append_addr = False

	if (append_addr):
		result.append(address)
		# Not writing the top 10,000 addresses to csv file for formatting purposes
		if (address not in top_ten_thousand_addrs):
			num_found = num_found + 1
			if (num_found % 50 == 0):
				print("Have written a total of ", num_found, " new addresses to CSV.")
			ls = [address]
			CSVwriter.writerow(ls)

	# top ten thousand addr -> next addr -> next addr -> next addr RETURN
	if (recursive_level > 2):
		return
	
	# Make the call to the API
	http_addr = "http://api.etherscan.io/api?module=account&action=txlist&address=" + address + "&sort=asc&apikey=" + my_key
	try:
		if (num_api_requests % 5 == 0):
			print("sleeping because making multiple of 5 API request: ", num_api_requests)
			time.sleep(1.0)
		num_api_requests = num_api_requests + 1
		# Note that we are making call to API for address
		already_called.append(address)
		url_file = url.urlopen(http_addr, data=None, timeout=10).read().decode('utf8')
	except urlerror.URLError:
		print ("ERROR HANDLING ADDRESS: ", address)
		return
	except socket.timeout:
		print ("The socket timed out for address: ", address)
		return
	
	# Handle the json returned by the API
	transactions = json.loads(url_file)["result"]
	if (transactions is None):
		return

	# Handles weird edge case where loads converts json to unicode string instead of list
	if (type(transactions) is not list):
		return
	
	# Find new addresses with which to make recursive calls
	seen = []
	for transaction in transactions:
		curr_from = transaction["to"]
		curr_to = transaction["from"]
		if (curr_from is curr_to):
			continue
		curr_addr = curr_to
		if (curr_addr == address):
			curr_addr = curr_from
		if ((curr_addr not in seen) and (curr_addr not in already_called)):
			seen.append(curr_addr)
	
	# Avoids creating duplicate recursive branches
	for addr in seen:		
		recursive_search(result, top_ten_thousand_addrs, addr, CSVwriter, recursive_level + 1)


def getAllAddresses(top_ten_thousand_addrs):
	result = []

	# Add addresses we've found previously to result
	with open("more_accounts.csv", 'rt') as csvfile:
		reader = csv.reader(csvfile)
		for addr in reader:
			result.append(addr[0])

	with open("dont_ruin_previous_progress.csv", 'w+') as writefile:
		CSVwriter = csv.writer(writefile)
		for index in range(1000, 10000):
			recursive_search(result, top_ten_thousand_addrs, top_ten_thousand_addrs[index], CSVwriter, 0)
	
	print(result)


if __name__ == '__main__':
  main()
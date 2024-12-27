import zstandard
import os
import json
import sys
from datetime import datetime
import logging.handlers


log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


def read_and_decode(reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0):
	chunk = reader.read(chunk_size)
	bytes_read += chunk_size
	if previous_chunk is not None:
		chunk = previous_chunk + chunk
	try:
		return chunk.decode()
	except UnicodeDecodeError:
		if bytes_read > max_window_size:
			raise UnicodeError(f"Unable to decode frame after reading {bytes_read:,} bytes")
		log.info(f"Decoding error with {bytes_read:,} bytes, reading another chunk")
		return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name):
	with open(file_name, 'rb') as file_handle:
		buffer = ''
		reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)
		while True:
			chunk = read_and_decode(reader, 2**27, (2**29) * 2)

			if not chunk:
				break
			lines = (buffer + chunk).split("\n")

			for line in lines[:-1]:
				yield line, file_handle.tell()

			buffer = lines[-1]

		reader.close()

def return_redd_objects(path: str) -> list[dict]:
	file_path = path
	file_size = os.stat(file_path).st_size
	file_lines = 0
	file_bytes_processed = 0
	created = None
	# field = "subreddit"
	# value = "wallstreetbets"
	bad_lines = 0
	objects = []
	authors = {}

	# try:
	for line, file_bytes_processed in read_lines_zst(file_path):
		try:
			obj = json.loads(line)
			created = datetime.utcfromtimestamp(int(obj['created_utc']))
			# temp = obj[field] == value
			objects.append(obj)

		except (KeyError, json.JSONDecodeError) as err:
			bad_lines += 1
		file_lines += 1
	
		if file_lines % 1000 == 0:
			print(f"\rReading {(file_bytes_processed / file_size) * 100:.0f}%", end="")
	print(f"Complete : {file_lines:,} : {bad_lines:,}")
	return objects
	
if __name__=="__main__":
	inpath = sys.argv[1]
	outpath = sys.argv[2]
	
	objs = return_redd_objects(inpath)
	
	with open(outpath, 'w') as f:
		f.write(json.dumps(objs, indent=2))

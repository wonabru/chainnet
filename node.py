import logging
import asyncio

from kademlia.network import Server

def run_kademlia_node(port):
	handler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	log = logging.getLogger('kademlia')
	log.addHandler(handler)
	log.setLevel(logging.DEBUG)


	loop = asyncio.get_event_loop()
	loop.set_debug(True)

	server = Server()
	loop.run_until_complete(server.listen(port))

	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	finally:
		server.stop()
		loop.close()

if __name__ == '__main__':
	run_kademlia_node(10023)
import logging


def run_kademlia_node(port, server, loop):

	handler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	log = logging.getLogger('kademlia')
	log.addHandler(handler)
	log.setLevel(logging.DEBUG)

	nodes = ["192.168.0.38", "192.168.56.1", "10.0.2.2", "10.0.2.15", "127.0.0.1"]
	bootstrap_node = []
	for n in nodes:
		bootstrap_node.append((n, port))

	loop.run_until_complete(server.listen(port))

	loop.run_until_complete(server.bootstrap(bootstrap_node))



if __name__ == '__main__':
	run_kademlia_node(port=10023)
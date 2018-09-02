#!/usr/bin/env python
# coding=utf-8

import os
import sys
import requests
from bs4 import BeautifulSoup

py2stdlib_filename = "./pystdlib2.db"
py3stdlib_filename = "./pystdlib3.db"
python2_stdlib_url = "https://docs.python.org/2.7/py-modindex.html"
python3_stdlib_url = "https://docs.python.org/3/py-modindex.html"
default_value = "default"

config = {
	"print_version": False,
	"require_filename": "requirements.txt",
}

def init_module_list_from_local():
	module_list = {}
	fd = None
	try:
		if sys.version_info[0] > 2:
			fd = open(py3stdlib_filename, "r")
		else:
			fd = open(py2stdlib_filename, "r")
		data = fd.read()
		for line in data.split("\n"):
			key_value = line.split(":")
			if len(key_value) == 2:
				module_list[key_value[0]] = key_value[1]
		pass
	except Exception as e:
		# raise e
		pass
	finally:
		if None != fd:
			fd.close()
		return module_list
		pass
def update_module_list():
	module_list = {}
	# length = 0
	try:
		html = ""
		if sys.version_info[0] > 2:
			html = requests.get(python3_stdlib_url).text
		else:
			html = requests.get(python2_stdlib_url).text
		soup = BeautifulSoup(html, "lxml")
		node_list = soup.select("code[class=\"xref\"]")
		for node in node_list:
			platform_info_node = node.parent.find_next_sibling("em")
			if None == node.string:
				continue
			# print node.string
			# print platform_info_node
			# print type(node.parent.next_sibling)
			if None == platform_info_node:
				module_list[node.string] = default_value
				# length += 1
			else:
				# print "[*] " + platform_info_node.string.strip("()")
				module_list[node.string] = platform_info_node.string.strip("()")
		pass
	except Exception as e:
		# raise e
		pass
	finally:
		# print "len = " + str(length)
		# exit(0)
		return module_list
		pass

def update_pystdlib_file(module_list):
	fd = None
	try:
		if sys.version_info[0] > 2:
			fd = open(py3stdlib_filename, "w")
		else:
			fd = open(py2stdlib_filename, "w")
		for key in module_list:
			fd.write(key + ":" + module_list[key] + "\n")
		pass
	except Exception as e:
		# raise e
		pass
	finally:
		if None != fd:
			fd.close()
		pass
def init_module_list():
	module_list = update_module_list()
	update_pystdlib_file(module_list)
	if len(module_list) == 0:
		module_list = init_module_list_from_local()
	return module_list

def detect_all_python_script(path):
	python_script_list = []
	for fpaths,dirs,fs in os.walk(path):
		for f in fs:
			file_path = os.path.join(fpaths,f)
			if file_path.endswith(".py"):
				print(file_path)
				python_script_list.append(file_path)
	return python_script_list

def is_local_module(path, module_name):
	if module_name.startswith("."):
		return True
	if os.path.exists(os.path.join(path, module_name)) or os.path.exists(os.path.join(path, module_name + ".py")):
		return True
	return False

def detect_import_modules(path):
	fd = None
	module_list = []
	try:
		fd = open(path, "r")
		for line in fd:
			line = line.strip()
			if line.startswith("import"):
				print("[+] " + line)
				module_list.extend(line.lstrip("import").strip().split(","))
			if line.startswith("from"):
				print("[+] " + line)
				module_name = line.split("import")[0].lstrip("from").strip()
				if not module_name.startswith("."):
					module_list.append(module_name)
		pass
	except Exception as e:
		raise e
	finally:
		if None != fd:
			fd.close()
		return module_list
		pass

def detect_all_import_modules(path):
	python_script_list = detect_all_python_script(path)
	module_list = []
	for script_file in python_script_list:
		module_list.extend(detect_import_modules(script_file))
	return module_list
def count_require_module(path, default_module_list, import_module_list):
	require_module_list = set()
	for module_name in import_module_list:
		if not is_local_module(path, module_name):
			if not module_name in default_module_list.keys():
				require_module_list.add(module_name)
	return require_module_list

def module_version(module_name):
	version = [""]
	try:
		script = 'import ' + module_name + '; version[0] = ' + module_name + '.__version__'
		exec(script, {"version": version})
		pass
	except Exception as e:
		# raise e
		pass
	return version[0]

def save_require_module_list(path, require_module_list):
	fd = None
	try:
		fd = open(os.path.join(path, config["require_filename"]), 'w')
		for module_name in require_module_list:
			fd.write(module_name)
			version = module_version(module_name)
			if "" != version and config["print_version"]:
				fd.write("==" + version)
			fd.write("\n")
		pass
	except Exception as e:
		raise e
	finally:
		if None != fd:
			fd.close()
		pass

def main(path):
	default_module_list = init_module_list()
	import_module_list = detect_all_import_modules(path)
	require_module_list = count_require_module(path, default_module_list, import_module_list)
	print(require_module_list)
	save_require_module_list(path, require_module_list)

if __name__ == '__main__':
	main("../save_html/")
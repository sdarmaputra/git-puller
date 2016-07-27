import os
import sys
import git
import json
import base64
import helper
import pprint
from shutil import copyfile
from docker import Client

printLog = helper.printLog

docker_client = Client(base_url = 'unix://var/run/docker.sock')
parent_dir = '/home/jiwa/tugasakhir/app-sandbox/'

class Puller(object):
	def __init__(self):
		printLog("Puller object created")

	# Create sanbox directory
	def setupDirectory(self, app_dir, www_dir):
		printLog("-------Starting Directory Operations!-------")
		printLog('Checking directory ', app_dir)
		if not os.path.exists(app_dir):
			printLog('Directory ', app_dir, " not exists. Creating it...")
			os.mkdir(app_dir)
		else:
			printLog('Directory ', app_dir, " already exists.")
		return

	# Create configuration files
	def createConfigurations(self, app_dir, config_file, custom_files):
		printLog("-------Starting Configuartion File Setup!-------")

		try:
			customFiles = json.loads(custom_files)
			for (key, item) in customFiles.items():
				customFilePath = os.path.join(app_dir, item["title"])
				customFileContent = base64.b64decode(item["content"])
				fcustom = open(customFilePath, 'w+')
				printLog("Writing to ", item["title"])
				fcustom.write(customFileContent)
				fcustom.close()
		except ValueError, e:
			printLog("Cannot load custom files: ", e)
			return

		return


	# Pull or clone application from VCS based on availability at local server
	def fetchFromRepo(self, repo_url, www_dir):
		printLog("-------Starting Git Activities!-------")
		if os.path.exists(www_dir):
			printLog("Application directory already exists!")
			printLog("Pulling from repository...")
			repo = git.cmd.Git(www_dir)
			repo.pull() # pull if directory exists
		else:
			printLog("Cloning repository...")
			git.Repo.clone_from(repo_url, www_dir) # clone if directory not exists yet
		return

	# Replace application's configuration files for production-like environment
	def setupConfigurations(self, app_dir, www_dir):
		printLog("-------Starting Configuration Activities!-------")
		# Get values from config.json
		configFilePath = os.path.join(app_dir, 'config.json')
		printLog("Looking for ", configFilePath)
		if (os.path.exists(configFilePath)):
			printLog("Configuration file found at ", configFilePath)
			with open(configFilePath) as data_file:
				try:
					configurations = json.load(data_file)
				except ValueError, e:
					printLog("Cannot load configuration: ", e)
					return

			# Replace configurations files
			for (target_file, config_file) in configurations["replace"].items():
				if os.path.exists(os.path.join(app_dir, config_file)):
					printLog("replacing", target_file, "with", config_file)
					copyfile(os.path.join(app_dir, config_file), os.path.join(www_dir, target_file))
				else:
					printLog("File not found:", os.path.join(app_dir, config_file))
			return
		else:
			printLog("File not found: config.json")
			return		

	# Create new docker container
	def createContainer(self, app_name, www_dir, app_port):
		printLog("-------Starting Container Creator Activities!-------")
		# Create docker container for application sandbox
		new_container = docker_client.create_container(image = "richarvey/nginx-php-fpm", 
			name = app_name,
			ports = [80],
			host_config = docker_client.create_host_config(
				port_bindings = {80 : app_port},
		    	binds = [www_dir + ":/usr/share/nginx/html"]
		    )
		)
		printLog("Docker creates:", new_container, " on port ", app_port)
		return

	# Set up sandbox for application virtualization
	def setupSandbox(self, app_name, www_dir, app_port):
		printLog("-------Starting Container Activities!-------")
		containers = docker_client.containers(all=True)
		
		# Check if container name already exists
		if any(container['Names'][0] == ('/' + app_name) for container in containers):
			printLog("Container already running!")
			printLog("Stopping container:", app_name)
			docker_client.stop(app_name)
			printLog("Removing container:", app_name)
			docker_client.remove_container(app_name)
			printLog("Recreating container:", app_name)
			self.createContainer(app_name, www_dir, app_port)
		else:
			printLog("No container available for those informations!")
			printLog("Creating container:", app_name)
			self.createContainer(app_name, www_dir, app_port)
		
		# Start application container
		docker_client.start(app_name)
		printLog("Starting container:", app_name)
		return

	# Initialize task
	def initTask(self, app_name, repo_url, app_port, config_file, custom_files):
		# Terminate program when no arguments presented
		if (app_name is None) or (repo_url is None):
			printLog("Please provide application name and repository URL!")
			sys.exit()
		else:
			www_dir = os.path.join(parent_dir, app_name, 'www') 
			app_dir = os.path.join(parent_dir, app_name)
			
			printLog("Initializing task...")
			printLog("Application name:", app_name)
			printLog("Repository URL:", repo_url)
			printLog("Application directory:", www_dir)
			
			self.setupDirectory(app_dir, www_dir)
			self.createConfigurations(app_dir, config_file, custom_files)
			self.fetchFromRepo(repo_url, www_dir)
			self.setupConfigurations(app_dir, www_dir)
			self.setupSandbox(app_name, www_dir, app_port)

def main():
	argv = sys.argv
	if (len(argv) < 2):
		printLog("Program terminated!")
		printLog("Usage: puller.py [application name] [repository url] [application port]")
		sys.exit()
	else:
		# Set up initial variables
		app_name = argv[1]
		repo_url = argv[2]
		app_port = argv[3]
		
		puller = Puller()
		puller.initTask(app_name, repo_url, app_port)

if __name__ == "__main__":
	main()
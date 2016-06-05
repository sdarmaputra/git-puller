import os
import sys
import git
import json
import helper
from shutil import copyfile
from docker import Client

printLog = helper.printLog

docker_client = Client(base_url = 'unix://var/run/docker.sock')
parent_dir = '/home/jiwa/tugasakhir/app-sandbox/'

# Pull or clone application from VCS based on availability at local server
def fetchFromRepo(repo_url, www_dir):
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
def setupConfigurations(app_dir, www_dir):
	# Get values from config.json
	with open(os.path.join(app_dir, 'config.json')) as data_file:
		configurations = json.load(data_file)

	# Replace configurations files
	for (target_file, config_file) in configurations["replace"].items():
		if os.path.exists(os.path.join(app_dir, config_file)):
			printLog("replacing", target_file, "with", config_file)
			copyfile(os.path.join(app_dir, config_file), os.path.join(www_dir, target_file))
		else:
			printLog("File not found:", os.path.join(app_dir, config_file))
	return		

# Create new docker container
def createContainer(app_name, www_dir):
	# Create docker container for application sandbox
	new_container = docker_client.create_container(image = "richarvey/nginx-php-fpm", 
		name = app_name,
		ports = [80],
		host_config = docker_client.create_host_config(
			port_bindings = {80 : 9001},
	    	binds = [www_dir + ":/usr/share/nginx/html"]
	    )
	)
	printLog("Docker creates:", new_container)
	return

# Set up sandbox for application virtualization
def setupSandbox(app_name, www_dir):
	containers = docker_client.containers()
	# Check if container name already exists
	if any(container['Names'][0] == ('/' + app_name) for container in containers):
		printLog("Container already exist!")
		printLog("Stopping container:", app_name)
		docker_client.stop(app_name)
		printLog("Removing container:", app_name)
		docker_client.remove_container(app_name)
		printLog("Recreating container:", app_name)
		createContainer(app_name, www_dir)
	else:
		printLog("Container not exist!")
		printLog("Creating new one...")
		createContainer(app_name, www_dir)
	
	# Start application container
	docker_client.start(app_name)
	printLog("Starting container:", app_name)
	return

# Initialize task
def initTask(app_name, repo_url):
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
		
		fetchFromRepo(repo_url, www_dir)
		setupConfigurations(app_dir, www_dir)
		setupSandbox(app_name, www_dir)

def main():
	argv = sys.argv
	if (len(argv) < 2):
		printLog("Program terminated!")
		printLog("Usage: puller.py [application name] [repository url]")
		sys.exit()
	else:
		# Set up initial variables
		app_name = argv[1]
		repo_url = argv[2]
		
		initTask(app_name, repo_url)

if __name__ == "__main__":
	main()
import tornado.ioloop
import tornado.web
from tornado import gen
from cStringIO import StringIO
from multiprocessing.pool import ThreadPool
import sys
import puller
import helper

printLog = helper.printLog
serverUrl = "http://10.151.36.93"
runningTask = []

_workers = ThreadPool(10)

def runBackground(function, callback, args=(), kwds={}):
	def _callback(result):
		tornado.ioloop.IOLoop.instance().add_callback(lambda: callback(result))
	_workers.apply_async(function, args, kwds, _callback)

def getTaskList(memory_file):
	taskList = []
	with open(memory_file) as memory:
		for line in memory:
			taskList.append(line.replace('\n', ''))
		memory.close()
	return taskList
	

def rewriteTaskList(memory_file, items=[]):
	memory = open(memory_file, 'w')
	for item in items:
		memory.write(item + '\n')
	memory.close()
	return

def startDeploy(appName, repoName, appPort, configFile, customFiles):
	taskList = getTaskList('runningTask.conf')

	if appName not in taskList:
		printLog('Task for', appName, 'started!')
		taskList = getTaskList('runningTask.conf')
		taskList.append(appName)
		rewriteTaskList('runningTask.conf', taskList)
		puller.initTask(appName, repoName, appPort, configFile, customFiles)
		return {'state': 'finished', 'status': 'success', 'app_name': appName, 'app_port': appPort, 'app_server': serverUrl}
	else:
		return {'state': 'running', 'status': 'running','app_name': appName, 'app_port': appPort, 'app_server': serverUrl}


class PullAndDeploy(tornado.web.RequestHandler):
	def get(self):
		self.write('Nothing to do.')

	@tornado.web.asynchronous
	def post(self):
		appName = self.get_argument('app_name')
		repoName = self.get_argument('repo_name')
		appPort = self.get_argument('app_port')
		configFile = self.get_argument('config_file', default=None)
		customFiles = self.get_argument('custom_files', default=None)

		runBackground(startDeploy, self.on_complete, (appName, repoName, appPort, configFile, customFiles))
		
	
	def on_complete(self, res):
		print res
		if (res.get('status') == 'success'):
			taskList = getTaskList('runningTask.conf')
			taskList.remove(res.get('app_name'))
			rewriteTaskList('runningTask.conf', taskList)
		
		self.write(res)
		self.finish()


def make_app():
	printLog("Application started")
	return tornado.web.Application([
		(r"/deploy", PullAndDeploy)
	])

if __name__ == "__main__":
	port = 8000
	rewriteTaskList('runningTask.conf', [])
	application = make_app()
	application.listen(port)
	printLog('Listening on port ' + str(port))
	tornado.ioloop.IOLoop.current().start()

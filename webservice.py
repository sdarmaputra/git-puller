import tornado.ioloop
import tornado.web
from tornado import gen
from cStringIO import StringIO
from multiprocessing.pool import ThreadPool
import sys
import puller
import helper

printLog = helper.printLog
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

def startDeploy(appName, repoName):
	taskList = getTaskList('runningTask.conf')

	if appName not in taskList:
		printLog('Task for', appName, 'started!')
		taskList = getTaskList('runningTask.conf')
		taskList.append(appName)
		rewriteTaskList('runningTask.conf', taskList)
		puller.initTask(appName, repoName)
		return {'status': 'success', 'app_name': appName}
	else:
		return {'status': 'running', 'app_name': appName}


class PullAndDeploy(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		appName = 'dokumentasi_lfs'
		repoName = 'https://github.com/sdarmaputra/dokumentasi_lfs.git'
		runBackground(startDeploy, self.on_complete, (appName, repoName))
		
	
	def on_complete(self, res):
		print res
		if (res.get('status') == 'success'):
			taskList = getTaskList('runningTask.conf')
			taskList.remove(res.get('app_name'))
			rewriteTaskList('runningTask.conf', taskList)
			self.write('Success!')
		else:
			self.write('Already running!')
		
		self.finish()


def make_app():
	printLog("Application started")
	return tornado.web.Application([
		(r"/deploy", PullAndDeploy)
	])

if __name__ == "__main__":
	port = 5000
	application = make_app()
	application.listen(port)
	printLog('Listening on port ' + str(port))
	tornado.ioloop.IOLoop.current().start()

import threading
import time

from internal import getLogger

class WorkerThread(threading.Thread):
    def __init__(self, func, *args):
        threading.Thread.__init__(self, name='Parsing')
        self.func = func
        self.args = args
        self._running = True
        self.start()

    def run(self):
        return self.func(*self.args)


class WorkerThreadPool():

    def __init__(self, threads=10, append=True):
        self.pool = []
        self._threads = threads
        self.__append = append

    def addThread(self, WorkerThread: WorkerThread):
        self.pool.append(WorkerThread)

    def delThread(self, WorkerThread: WorkerThread):
        self.pool.remove(WorkerThread)

    def __cleanPool(self):
        for x in self.pool:
            self.delThread(x)

    def isAllThreadsDone(self):
        while True:
            time.sleep(1)
            if all(x.is_alive() == False for x in self.pool):
                return
            continue

    def __Tany(self, func, results, *args):
        if self.__append:
            results.append(func(*args))
        else:
            results.extend(func(*args))
        getLogger().debug("added to the results")
        return True

    def anyThread(self, func, links, *args):
        results = []

        while True:
            for x in range(self._threads):
                try:
                    thread = WorkerThread(self.__Tany, func, results, links.pop(), *args)
                    self.addThread(thread)
                except IndexError:
                    getLogger().debug("threads for the pages are done")
                    break
            self.isAllThreadsDone()
            if not len(links):
                break

        self.__cleanPool()
        return results
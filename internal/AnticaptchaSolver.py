from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask


class AntiCaptchaSolver():
    def __init__(self, api_key):
        self.__client = AnticaptchaClient(api_key)

    def __createTask(self, task):
        return self.__client.createTask(task)

    def solveTask(self, website_url, website_key):
        job = self.__createTask(NoCaptchaTaskProxylessTask(website_url, website_key))
        job.join()
        return job.get_solution_response()

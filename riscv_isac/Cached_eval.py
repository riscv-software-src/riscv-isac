import inspect


class Cached_eval:
	def __init__(self,fun):
		self.function = fun
		fun_info = inspect.getargspec(fun)
		self.args = fun_info.args
		self.defaults = fun_info.defaults
		if self.defaults is not None:
			self.defaults = list(self.defaults)
		self.func_cache = {}

	def process_args(self,args,kwargs):
		arg_list = []
		for arg in args:
			arg_list.append(arg)

		total_args = len(self.args)
		for i in range(len(arg_list),total_args):
			if self.args[i] in kwargs.keys():
				arg_list.append(kwargs[self.args[i]])
			else:
				arg_list.append(self.defaults[i-total_args])
		return tuple(arg_list)

	def __call__(self,*args,**kwargs):
		argument = self.process_args(args,kwargs)
		if self.func_cache.get(argument,None) is not None:
			# print("Found in cache")
			return self.func_cache[argument]

		# print("Not found")
		val = self.function(*args,**kwargs)
		self.func_cache[argument] = val
		return val

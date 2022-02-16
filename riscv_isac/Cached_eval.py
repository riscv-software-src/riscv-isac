from collections import OrderedDict
import inspect

class lru_cache:
	def __init__(self,count):
		self.dict = OrderedDict()
		self.max_entry = count

	def __getitem__(self,key):
		try:
			ret = self.dict[key]
			self.dict.move_to_end(key)
			return ret
		except :
			raise KeyError

	def __setitem__(self,key,value):
		self.dict[key] = value
		self.dict.move_to_end(key)
		# Check if we have exceeded number of cache entries
		# If yes, remove top item as most recent is pushed to back
		if len(self.dict) > self.max_entry :
			self.dict.popitem(last=False)


	def get(self,key,default=None):
		try :
			return self.__getitem__(key)
		except:
			return default


	def set(self,key,value):
		self.__setitem__(key,value)


class Lazy_eval:
	def __init__(self,fun):
		self.function = fun
		fun_info = inspect.getargspec(fun)
		self.args = fun_info.args
		self.defaults = fun_info.defaults
		if self.defaults is not None:
			self.defaults = list(self.defaults)
		self.func_cache = lru_cache(32)

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

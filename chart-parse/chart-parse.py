# -*- coding: utf-8 -*

#目的：实现自底向上句法分析
#参考资料：
#    计算语言学讲义(07)句法分析(一).pdf
#    计算语言学讲义(08)句法分析(二).pdf https://wenku.baidu.com/view/646ea106de80d4d8d15a4f47.html?sxts=1548945407400
#    计算语言学讲义(09)句法分析(三).pdf https://wenku.baidu.com/view/9a27478371fe910ef12df854.html?sxts=1548945436887
#    https://ilewseu.github.io/2018/07/08/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E5%A4%84%E7%90%86%E5%9F%BA%E7%A1%80-%E5%8F%A5%E6%B3%95%E5%88%86%E6%9E%90/
#    http://blog.sina.com.cn/s/blog_6791f80e0100l3mi.html

import re

class Constituent:
	'''成分类，用于存储单词或短语组成的句子成分'''
	start = 0      #成分的起始位置
	end = 0        #成分的结束位置
	key = None     #成分代表的单词
	value = ""     #成分的词性
	childcons = [] #成分的子成分

	def __init__(self, start, end, key, value, childcons):
		self.start = start
		self.end = end
		self.key = key
		self.value = value
		self.childcons = childcons

	def GetChildren(self):
		str = ""
		if self.key:
			str = self.key
		if self.childcons:
			for con in self.childcons:
				str = str + " " + con.GetChildren()
		return str.strip()

	def ToString(self):
		'''将成分转为字符串形式'''
		return "((%s<%s>), %d, %d)" % (self.value, self.GetChildren(), self.start, self.end)

class Arc:
	'''短语边类，用于存储短语结构'''
	start = 0       #边的起始位置
	end = 0         #边的结束位置
	position = 0    #边的当前位置
	grammars = []   #边代表的短语语法
	pargrammar = "" #边代表短语语法的上一级分类
	childcons = []  #边包含的子成分

	def __init__(self, start, end, curgrammar, pargrammar, position, childcons):
		self.start = start
		self.end = end
		self.position = position
		self.grammars = curgrammar
		self.pargrammar = pargrammar
		self.childcons = childcons

	def IsActive(self):
		return self.position < len(self.grammars)

	def CanExtend(self, constituent):
		'''当前边，按给定成分是否可扩展'''
		if self.grammars[self.position] == constituent.value:
			#'边的结束位置与成分的起始位置能接上' 或 '边的范围与成分相同'
			if (self.end == constituent.start and self.position != 0) or (self.start == constituent.start and self.end == constituent.end and self.position == 0):
				return True
		return False

	def Extend(self, constituent):
		'''按给定成分，扩展当前边'''
		self.end = constituent.end
		self.position = self.position+1
		self.childcons.append(constituent)
		return self

	def CreateNewConsitutent(self):
		'''将当前边（非活动），形成新的成分'''
		return Constituent(self.start, self.end, None, self.pargrammar, self.childcons)

	def ToString(self):
		'''将当前边生成字符串形式'''
		str = ""
		for index, word in enumerate(self.grammars):
			if index == self.position:
				str = str + u"•"
			str = str + word + ' '
		str = str.strip()
		if not self.IsActive():
			str = str + u'•'
		return "((%s), %d, %d)" % (str, self.start, self.end)

class BottomToUpChartParser:
	'''自底向上实现句子成分解析类'''
	dictionary = {} #字典表
	grammars = {}   #语法表
	words = []      #待解析句子形成的单词列表
	chart = {}      #线图，用于存储所有边结构
	agenda = []     #待处理成分形成的待处理表
	result = None   #句子成分处理结果
	index = 0       #当前处理句子中的位置
	step = 1        #处理步骤的编号

	def __init__(self, dictionary, grammars):
		self.dictionary = dictionary
		self.grammars = grammars

	def ParseSentence(self, sentence):
		'''解析句子结构'''
		if not sentence:
			print("ERROR: can not parse null sentence:" . sentence)
			return

		self.words = sentence.lower().split()
		for word in self.words:
			self.PutWordToAgenda(word)
			self.HandleAgenda()

	def PutWordToAgenda(self, word):
		'''将单词的每一个词性生成成分，并放入待处理表中'''
		for item in self.dictionary[word]:
			self.agenda.append(Constituent(self.index, self.index+1, word, item, None))
		self.index = self.index + 1

	def HandleAgenda(self):
		'''处理待处理表'''
		while True:
			if not self.agenda:
				return
			text = "\n#Step[%02d] - 待处理表：" % self.step
			for con in self.agenda:
				text = text + con.ToString() + "; "
			print(text)
			text = u"              活动边："
			num = 0
			for arc in self.chart.values():
				text = text + arc.ToString() + "; "
				num = num + 1
				if num % 4 == 0:
					text = text + "\n\t\t      "
			print(text.rstrip())
			print("--------------------------------------------------------------------------------------------------")
			constituent = self.agenda.pop(0)
			print("\t->获取新成分：" + constituent.ToString())
			self.CreateActiveArc(constituent)
			self.ExtendActiveArc(constituent)
			self.step = self.step + 1

	def CreateActiveArc(self, constituent):
		'''查语法表将成分生成活动边'''
		find = False
		#查语法表里所有语法
		for key, phrases in self.grammars.items():
			#查语法对应的短语
			for phrase in phrases:
				if re.match(constituent.value + " .*", phrase):
					#将以当前成分开头的短语生成活动边
					arc = Arc(constituent.start, constituent.end, phrase.split(), key, 0, [])
					self.chart[arc.ToString()] = arc
					print(u"\t->生成活动边: " + arc.ToString())
					find = True
		if not find:
			print(u"\t->生成活动边: 没有找到匹配的短语")

	def ExtendActiveArc(self, constituent):
		'''扩展所有按当前成分可扩展的活动边'''
		find = False
		for key,arc in self.chart.items():
			if arc.IsActive() and arc.CanExtend(constituent):
				#扩展活动边
				arc.Extend(constituent)
				print(u"\t->移进活动边: %s -> %s" % (key, arc.ToString()))
				self.chart[arc.ToString()] = arc
				del self.chart[key]
				find = True

				#将扩展后形成的非活动边，形成新的成分
				if not arc.IsActive():
					newcon = arc.CreateNewConsitutent()
					print(u"\t->规约新成分: %s -> %s" % (arc.ToString(), newcon.ToString()))
					if newcon.start == 0 and newcon.end == len(self.words):
						del self.agenda[:]
						self.result = newcon
						print("\t->新成分能够覆盖整个句子，解析结束!!!")
						break
					else:
						self.agenda.append(newcon)
		if not find:
			print("\t->移进活动边: 未找到可移进活动边")

	def DrawPicture(self):
		'''将解析的句子结构生成图片'''
		try:
			import pygraphviz as pgv
		except ImportError:
			print("ERROR: no pygraphviz installed, please run:")
			print("sudo apt-get install graphviz libgraphviz-dev pkg-config")
			print("sudo pip install pygraphviz")
			return

		graph = pgv.AGraph(label='Parse: ' + ' '.join(self.words), directed=True, strict=True, epsilon='0.001')
		graph.add_node("%d-%s" % (0, self.result.value), label=self.result.value)
		self.PicAddNode(graph, self.result, 0)
		graph.layout('dot')
		graph.draw('test.jpg', format = 'jpg')
		print("\nSave picture of sentence struct to test.jpg")

	def PicAddNode(self, graph, constituent, level):
		'''将成分关系画成图'''
		if not constituent.childcons:
			return
		for childcon in constituent.childcons:
			par_node_name = "%d-%s" % (level, constituent.value)
			child_node_name = "%d-%s" % (level+1, childcon.value)
			child_node_label = childcon.value
			if childcon.key:
				child_node_label = child_node_label + "\n(%s)" % childcon.key

			graph.add_node(child_node_name, label=child_node_label)
			graph.add_edge(par_node_name, child_node_name)
			self.PicAddNode(graph, childcon, level+1)

	def ShowNode(self):
		'''以文本形式画句子结构图'''
		text = "0:          "
		text = text + self.result.value
		print(text)

		text = "1:     "
		for con1 in self.result.childcons:
			text = text + con1.value + "       "
		print(text)

		text = "2:"
		for con1 in self.result.childcons:
			for con2 in con1.childcons:
				text = text + con2.value + " "
			text = text + "  "
		print(text)

		text = "3:     "
		for con1 in self.result.childcons:
			for con2 in con1.childcons:
				if con2.childcons:
					for con3 in con2.childcons:
						text = text + con3.value + " "
				text = text + "  "
			text = text + "  "
		print(text)

		text = "4:      "
		for con1 in self.result.childcons:
			for con2 in con1.childcons:
				if con2.childcons:
					for con3 in con2.childcons:
						if con3.childcons:
							for con4 in con3.childcons:
								text = text + con4.value + " "
						text = text + "  "
				text = text + "  "
		print(text)

#Main Function
dictionary = {
	'the'   : ['ART'],
	'large' : ['ADJ'],
	'can'   : ['N', 'AUX', 'V'],
	'hold'  : ['N', 'V'],
	'water' : ['N', 'V']
	}
grammars = {
	'S'   : ['NP VP'],
	'NP'  : ['ART ADJ N', 'ART N', 'ADJ N'],
	'VP'  : ['AUX VP', 'V NP']
	}
sentence = 'The large can can hold the water'

print(u"待处理的句子：" + sentence)
parser = BottomToUpChartParser(dictionary, grammars)
parser.ParseSentence(sentence)

print(u"\n语法结构树：")
parser.ShowNode()
parser.DrawPicture()

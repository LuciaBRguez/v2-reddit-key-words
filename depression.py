import json
import io
import re
import os
import networkx as nx
import operator
import math, random, sys, csv


class PageRank:
	def __init__(self, graph, directed):
		self.graph = graph
		self.V = len(self.graph)
		self.d = 0.85
		self.directed = directed
		self.ranks = dict()

	def rank(self):
		for key, node in self.graph.nodes(data=True):
			if self.directed:
				self.ranks[key] = 1 / float(self.V)
			else:
				self.ranks[key] = node.get('rank')

		for _ in range(10):
			for key, node in self.graph.nodes(data=True):
				rank_sum = 0
				curr_rank = node.get('rank')
				if self.directed:
					neighbors = self.graph.out_edges(key)
					for n in neighbors:
						outlinks = len(self.graph.out_edges(n[1]))
						if outlinks > 0:
							rank_sum += (1 / float(outlinks)) * self.ranks[n[1]]
				else:
					neighbors = self.graph[key]
					for n in neighbors:
						if self.ranks[n] is not None:
							outlinks = len(self.graph.neighbors(n))
							rank_sum += (1 / float(outlinks)) * self.ranks[n]

				# actual page rank compution
				self.ranks[key] = ((1 - float(self.d)) * (1 / float(self.V))) + self.d * rank_sum

		return p


def rank(graph, node):
	# V
	nodes = graph.nodes()
	# |V|
	nodes_sz = len(nodes)
	# I
	neighbs = graph.neighbors(node)
	# d
	rand_jmp = random.uniform(0, 1)

	ranks = []
	ranks.append((1 / nodes_sz))

	for n in nodes:
		rank = (1 - rand_jmp) * (1 / nodes_sz)
		trank = 0
		for nei in neighbs:
			trank += (1 / len(neighbs)) * ranks[len(ranks) - 1]
		rank = rank + (d * trank)
		ranks.append(rank)


regex = re.compile('[^a-zA-Z]')

"Numero de palabras totales en Depression"
numDepression = 0
"Array con todas las palabras de Depression"
palabrasDepression = []
"Array con palabras vacias"
stopWords = []
"Array con las palabras de Depression sin vacias"
depressionNonStopWords = []


dictRanksRootLLR = {}
dictRanksPageRank = {}
dictRanksPageRankNoNulos = {}


"Se abre el archivo depression.json con las 10.000 entradas de depression"
with open('depression.json') as json_file:
	data = json.load(json_file)
data= data['data']


"Se anaden palabras vacias a stopWords"
with io.open("stopWords.txt", mode="r", encoding="utf-8") as fstopWords:
	for line in fstopWords:
		if "|" in line:
			p = line.split("|")
			p0 = re.sub(' +', '', p[0])
			if p0 != "":
				stopWords.append(p0)
		else:
			p = line.split("\n")
			if p[0] != "":
				if "'" in p[0]:
					p[0] = line.split("'")
					if p[0] not in stopWords:
						stopWords.append(p[0][0])
					p01 = re.sub('\n', "", p[0][1])
					if p01 not in stopWords:
						stopWords.append(p01)
				elif p[0] not in stopWords:
					stopWords.append(p[0])
fstopWords.close()


"Se escriben los datos sin limpiar en depression.txt"
with io.open("depression.txt", mode="w", encoding="utf-8") as fdepression:
	for elemento in data:
		if 'selftext' in elemento:
			fdepression.write(elemento['title'] + "\n" + elemento['selftext']+ "\n")
		else:
			fdepression.write(elemento['title'] + "\n")
fdepression.close()


"Se eliminan URLs y sustituyen los caracteres no alfabeticos por espacios"
with io.open("depression.txt", mode="r", encoding="utf-8") as fdepression:
	with io.open("depressionAux.txt", mode="w", encoding="utf-8") as fdepressionAux:
		for line in fdepression:
			palabras = line.split()
			for p in palabras:
				if not "www." in p and not "http" in p and not "deletd" in p and not "removed" in p:
					if not p.isalpha():
						pnew = re.sub('[^a-zA-Z]+', ' ', p)
						fdepressionAux.write(pnew.lower() + ' ')
					else:
						fdepressionAux.write(p.lower() + ' ')
			fdepressionAux.write("\n")
	fdepressionAux.close()
fdepression.close()

"Se eliminan los espacios multiples"
with io.open("depressionAux.txt", mode="r", encoding="utf-8") as fdepressionAux:
	with io.open("depressionClean.txt", mode="w", encoding="utf-8") as fdepressionClean:
		for line in fdepressionAux:
			palabras = line.split()
			for p in palabras:
				pnew = re.sub(' +', ' ', p)
				palabrasDepression.append(pnew)
				fdepressionClean.write(pnew + ' ')
				numDepression += 1
			fdepressionClean.write("\n")
	fdepressionClean.close()
fdepressionAux.close()
os.remove("depressionAux.txt")


"PAGE RANK"
"Se crea una grafica"
G = nx.Graph()

"PAGE RANK SIN PALABRAS NULAS"
"Se anaden todos los nodos"
for p in palabrasDepression:
	G.add_node(p)

"Se recorren las lineas para anadir edges en donde se ignoran las palabras nulas"
with io.open("depressionClean.txt", mode="r", encoding="utf-8") as fdepressionClean:
	for line in fdepressionClean:
		palabras = line.split()
		for i in range(0, len(palabras)):
			if i<=(len(palabras)-15):
				for j in range(i, i+15):
					for k in range(j+1, i+15):
						"Las palabras nulas no se anaden como edges"
						if palabras[j] not in stopWords and palabras[k] not in stopWords:
							G.add_edge(palabras[j], palabras[k])
fdepressionClean.close()

"Se aplica PageRank"
with io.open("pageRankNoNulos.txt", mode="w", encoding="utf-8") as fpageRankNoNulos:
	isDirected = False
	p = PageRank(G, isDirected)
	p.rank()
	sorted_r = sorted(p.ranks.items(), key=operator.itemgetter(1), reverse=True)
	for tup in sorted_r:
		fpageRankNoNulos.write(str(tup[0]) + "\t" +str(tup[1]) + "\n")
fpageRankNoNulos.close()


"PAGE RANK CON PALABRAS NULAS"
"Se eliminan todos los nodes y edges"
G.clear()
"Se anaden todos los nodos"
for p in palabrasDepression:
	G.add_node(p)

"Se recorren las lineas para anadir edges en donde de palabras nulas y no nulas"
with io.open("depressionClean.txt", mode="r", encoding="utf-8") as fdepressionClean:
	for line in fdepressionClean:
		palabras = line.split()
		for i in range(0, len(palabras)):
			if i<=(len(palabras)-15):
				for j in range(i, i+15):
					for k in range(j+1, i+15):
						G.add_edge(palabras[j], palabras[k])
fdepressionClean.close()

"Se aplica PageRank"
with io.open("pageRank.txt", mode="w", encoding="utf-8") as fpageRank:
	isDirected = False
	p = PageRank(G, isDirected)
	p.rank()
	sorted_r = sorted(p.ranks.items(), key=operator.itemgetter(1), reverse=True)
	for tup in sorted_r:
		"No se escriben las palabras nulas"
		if tup[0] not in stopWords:
			fpageRank.write(str(tup[0])+ "\t" + str(tup[1]) + "\n")
fpageRank.close()


"Se crea un Dictionary con los ranks de PageRank"
with io.open("pageRank.txt", mode="r", encoding="utf-8") as franksPageRank:
	rank = 0
	for line in franksPageRank:
		p = line.split("\t")
		rank += 1
		dictRanksPageRank[p[0]] = rank
franksPageRank.close()


"Se crea un Dictionary con los ranks de PageRankNoNulos"
with io.open("pageRankNoNulos.txt", mode="r", encoding="utf-8") as franksPageRankNoNulos:
	rank = 0
	for line in franksPageRankNoNulos:
		p = line.split("\t")
		rank += 1
		dictRanksPageRankNoNulos[p[0]] = rank
franksPageRankNoNulos.close()


"Se crea un Dictionary con los ranks de RootLLR"
with io.open("rootLLR.txt", mode="r", encoding="utf-8") as frootLLR:
	rank = 0
	for line in frootLLR:
		p = line.split("\t")
		if p[0] in dictRanksPageRank:
			rank += 1
			dictRanksRootLLR[p[0]] = rank
frootLLR.close()


"Coeficiente de Spearman"
with io.open("coefSpearman.txt", mode="w", encoding="utf-8") as fcoefSpearman:
	for k, v in dictRanksRootLLR.items():
		fcoefSpearman.write(k + "\t" + str(v) + "\t" + str(dictRanksPageRank[k]) + "\t" + str(dictRanksPageRankNoNulos[k]) + "\n")
fcoefSpearman.close()
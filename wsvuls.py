import requests
import re
import sys
import argparse
import hashlib
import uuid
import json



f = open('./db/vulners.json')
loaded = json.load(f)

end = '\033[1;0m'
R = '\033[1;91m'
G = '\033[1;92m'

URL = loaded["base"]["url"]+loaded["base"]["endpoint"]
sync = loaded["base"]["url"]+loaded["base"]["scanner"]

def generate_phpsession():
	nosalted="anouarbensaad"
	result = hashlib.md5(nosalted.encode())
	return str("b"+result.hexdigest())

def parser_error(errmsg):
    print("Usage: python " + sys.argv[0] + " [Options] use -h for help")
    print(R + "Error: " + errmsg + W)
    sys.exit()

def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython3 ' + sys.argv[0] + " -u google.com")
    parser.error = parser_error
    parser._optionals.title = "\nOPTIONS"
    parser.add_argument('-u', '--url', help="url target to scan")
    parser.add_argument('-m', '--mapper', help="map all requests details...", dest='mapper',action="store_true")
    return parser.parse_args()

args = parse_args()
URL_ARG = args.url
MAPPER_ARG = args.mapper


def getnonce(data):
	regexp=re.compile(r'\"nonce\":\"(.+)\"')
	matched=re.search(regexp,data)
	print("retrieve token",matched.group(1))
	return matched.group(1)

def postwvscan(nonce):
	sess_id = uuid.uuid1()
	data={
	"action":"web_scanner",
	"url":URL_ARG,
	"nonce_code":nonce
	}
	anonumous_session="\""+str(sess_id)+"\""
	cookies= {
	"ajs_anonymous_id": anonumous_session,
	"PHPSESSID": generate_phpsession(),
	"vid": str(sess_id)
	}
	headers={
	"X-Requested-With": "XMLHttpRequest",
	"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
	"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
	"Accept": "*/*",
	"Host": "snyk.io",
	"Referer": URL,
	"Connection": "keep-alive"
	}
	posted=requests.post(sync,headers=headers,data=data,cookies=cookies)
	return posted.json()

HEADERS={
"Content-Type": "*/*",
"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}
res = requests.get(URL,headers=HEADERS);

def getAverages(res):
	text="...."
	analysed=False
	response=None
	print("AnalyseID: %s " % (res["data"]["testId"]))
	analyseURL = res["data"]["jsonUrl"]
	print("\n[ Start Scanning For %s]\n" % (URL_ARG))
	while not analysed:
		res_analyse = requests.get(analyseURL)
		try:
			estimation = res_analyse.json()["statusText"]
			for x in text:
				sys.stdout.write(x)
				sys.stdout.write("")
				sys.stdout.flush() 
			if estimation == "Test Complete":
				analysed=True
				return res_analyse.json()["data"]["runs"]["1"]["firstView"]["pages"]["details"]
		except KeyError as err:
			analysed=True
			return res_analyse.json()["data"]["runs"]["1"]["firstView"]["pages"]["details"]

def netspeed(url):
	print("\n")
	response = requests.get(url)
	return response.text

def getTTFB(data):
	regexp = r'<td id=\"TTFB\" valign=\"middle\">(.+)<span class=\"units\">(.+)</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		ttfb_value = matched.group(1)
		return ttfb_value
	except Exception as err:
		return None

def getStartRender(data):
	regexp = r'<td id=\"StartRender\" valign=\"middle\">(.+)<span class=\"units\">(.+)</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		start_render = matched.group(1)
		return start_render
	except Exception as err:
		return None

def getfirstContentfulPaint(data):
	regexp = r'<td id=\"firstContentfulPaint\" valign=\"middle\">(.+)<span class=\"units\">(.+)</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		getfirstContentfulPaint = matched.group(1)
		return getfirstContentfulPaint
	except Exception as error:
		return None

def getSpeedIndex(data):
	regexp = r'<td id=\"SpeedIndex\" valign=\"middle\">(.+)<span class=\"units\">(.+)</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		SpeedIndex = matched.group(1)
		return SpeedIndex
	except Exception as error:
		return None

def getLargestContentfulPaint(data):
	regexp = r'<td id="chromeUserTiming.LargestContentfulPaint" class=".+" valign="middle">(.+)<span class="units">S</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		LCP = matched.group(1)
		return LCP
	except Exception as error:
		return None

def getCumulativeLayoutShift(data):
	regexp = r'<td id="chromeUserTiming.CumulativeLayoutShift" class=".+" valign="middle">(.+)</td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		LCP = matched.group(1)
		return LCP
	except Exception as error:
		return None

def getTotalBlockingTime(data):
	regexp = r'<td id="TotalBlockingTime" class=".+" valign="middle"><span class="units comparator">.+</span>(.+)<span class="units">S</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		TBT = matched.group(1)
		return TBT
	except Exception as error:
		return None

def getDocComplete(data):
	regexp = r'<td id="DocComplete" class="border" valign="middle">(.+)<span class="units">S</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		DC = matched.group(1)
		return DC
	except Exception as error:
		return None

def getRequestDoc(data):
	regexp = r'<td id="RequestsDoc" valign="middle">(.+)</td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		RD = matched.group(1)
		return RD
	except Exception as error:
		return None

def getBytesInDoc(data):
	regexp = r'<td id="BytesInDoc" valign="middle">(.+)<span class="units">KB</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		BID = matched.group(1)
		return BID
	except Exception as error:
		return None

def getFullyLoaded(data):
	regexp = r'<td id="FullyLoaded" class="border" valign="middle">(.+)<span class="units">S</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		FL = matched.group(1)
		return FL
	except Exception as err:
		return None

def getRequestsCount(data):
	regexp = r'<td id="Requests" valign="middle">(.+)</td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		RC = matched.group(1)
		return RC
	except Exception as err:
		return None

def getByteIn(data):
	regexp = r'<td id="BytesIn" valign="middle">(.+)<span class="units">KB</span></td>'
	rempiled = re.compile(regexp)
	matched=re.search(rempiled,data)
	try:
		BI = matched.group(1)
		return BI
	except Exception as err:
		return None

def requestsMapper(data):
	MAPPED_REQUESTS = re.compile(r'<tr><th class="reqNum(?:\s+)(.+)(?:\s+)?.+"><a href=".+">(.+)</a></th>\s+<td class="reqUrl.+"><a rel="nofollow" href="(.+)".+</a></td>\s+<td class="reqMime.+">(.+)</td>\s+<td class="reqStart.+">(.+)</td>\s+<td class="reqDNS(?:\s+)?.+>(.+)</td>\s+<td class="reqSocket.+">(.+)</td>\s+<td class="reqSSL.+">(.+)</td>\s+<td class="reqTTFB.+">(.+)</td>\s+<td class="reqDownload.+">(.+)</td>\s+<td class="reqBytes.+">(.+)</td>\s+<td class="cpuTime.+">(.+)</td>\s+<td class="reqResult.+">(.+)</td>\s+<td class="reqIP.+">(.+)</td>\s+</tr>')
	find_requests = re.findall(MAPPED_REQUESTS,data)
	return find_requests

def parse_requests(content,debug):
	for c in content:
		dbglen = len(c[0].split(" "))
		if (dbglen == 2):
			if( c[0].split(" ")[0] == "warning" ):
				print("%sreqNum:%s%s" % (R,c[1],end))
				print("%sreqUrl:%s%s" % (R,c[2],end))
				print("%sreqMime:%s%s" % (R,c[3],end))
				print("%sreqStart:%s%s" % (R,c[4],end))
				print("%sreqBytes: %s%s" % (R,c[10],end))
				print("%sreqIP: %s%s" % (R,c[13],end))
				print("−−−−−−−−−−−−\n")
		else:
			print(f"reqNum: {c[1]}")
			print(f"reqUrl: {c[2]}")
			print(f"reqMime: {c[3]}")
			print(f"reqStart: {c[4]}")
			print(f"reqBytes: {c[10]}")
			print(f"reqResult: {c[12]}")
			print(f"reqIP: {c[13]}")
			print("−−−−−−−−−−−−\n")


if __name__ == '__main__':
	process_load = getAverages(postwvscan(getnonce(res.text)))
	data_content = netspeed(process_load)
	# print(data_content)
	if getTTFB(data_content) is not None:
		print(f"First Byte : {getTTFB(data_content)} Seconds")
	if getStartRender(data_content) is not None:
		print(f"Start Render : {getStartRender(data_content)} Seconds")
	if getfirstContentfulPaint(data_content) is not None:
		print(f"FCP : {getfirstContentfulPaint(data_content)} Seconds")
	if getSpeedIndex(data_content) is not None:
		print(f"Speed Index : {getSpeedIndex(data_content)} Seconds")
	if getLargestContentfulPaint(data_content) is not None:
		print(f"LCP : {getLargestContentfulPaint(data_content)} Seconds")
	if getCumulativeLayoutShift(data_content) is not None:
		print(f"CLS : {getCumulativeLayoutShift(data_content)}")
	if getTotalBlockingTime(data_content) is not None:
		print(f"TBT : {getTotalBlockingTime(data_content)} Seconds")
	if getDocComplete(data_content) is not None:
		print(f"DC Time : {getDocComplete(data_content)} Seconds")
	if getRequestDoc(data_content) is not None:
		print(f"DC Requests : {getRequestDoc(data_content)}")
	if getBytesInDoc(data_content) is not None:
		print(f"DC Bytes : {getBytesInDoc(data_content)} KiloBytes")
	if getFullyLoaded(data_content) is not None:
		print(f"Time : {getFullyLoaded(data_content)} Seconds")
	if getRequestsCount(data_content) is not None:
		print(f"Requests : {getRequestsCount(data_content)}")
	if getByteIn(data_content) is not None:
		print(f"Total Bytes : {getByteIn(data_content)} KiloBytes")
	if (MAPPER_ARG):
		print("\n[ Request Details ]")
		parse_requests(requestsMapper(data_content),"")
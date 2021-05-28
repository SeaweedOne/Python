import hashlib #보안 및 메세지 요약 알고리즘 인터페이스
import time #날짜 시간 모듈
import csv #csv 파일 컨트롤 모듈
import random
from http.server import BaseHTTPRequestHandler, HTTPServer #서버 띄우기 위한 라이브러리
from socketserver import ThreadingMixIn #네트워크 서버 작성 작업 단순 (클래스는 동기적으로 요청을 처리..느리다.. 요청을 처리하기 위해 별도의 프로세스나 스레드를 만들자!ThreadingMixIn 믹스인 클래스를 사용하여 비동기 동작을 지원)
import json # JSON 문자열을 읽거나, HTTP 요청의 전문(body)을 읽을 때 자주 사용 , Python 객체를 JSON 문자열로 변환하기 위해서는 dumps() 함수를 사용
import re #정규표현식
from urllib.parse import parse_qs
from urllib.parse import urlparse #url 파싱 라이브러리 (문자열을 구성요소로 분리)
#여러분이 사용하는 PC에는 윈도우, macOS, 리눅스와 같은 운영체제가 설치되어 있습니다. 운영체제는 컴퓨터를 전체적으로 관리하는 매니저 역할을 합니다. 우리가 프로그램이라고 부르는 것들은 운영체제 위에서 동작합니다. 프로그램이 메모리에 올라가서 실행 중인 것을 프로세스(process)라고 부릅니다. 프로세스의 실행 단위를 스레드라고 합니다. 프로세스는 최소 하나 이상의 스레드를 갖으며 경우에 따라 여러 스레드를 가질 수도 있습니다.
import threading #스레드 컨트롤
import cgi #웹서버와 언어간의 쉬운 연동을 위한 표준화된 약속 > cgi(common gateway interface)
import uuid #universally unique identifier #가장 유일한 번호구하기
from tempfile import NamedTemporaryFile #임시파일/디렉토리 생성 모듈  TemporaryDirectory 자동 정리를 제공하고 컨텍스트 관리자로 사용할 수 있음. 임시 저장 영역으로 사용할 수 있는 파일류 객체를 반환
import shutil #파일 및 디렉터리 작업을 수행
import requests #ython에서 HTTP 요청을 보내는 모듈 # for sending new block to other nodes
import pandas as pd

# 20190605 /(YuRim Kim, HaeRi Kim, JongSun Park, BohKuk Suh , HyeongSeob Lee, JinWoo Song)
#프로세스를 만들어주는 라이브러리
#프로세스가 서로 간섭하지 않도록 Lock 객체를 사용 -> 어떤 자원에 두 스레드가 동시에 사용하려고 할 때 먼저 락을 선점하려고 .acquire()를 호출 할 것이다. 선점한 스레드는 자원을 사용할 수 있다, 하지만 같이 사용하려고 접근하던 다른 스레드의 진행은 멈추게 되고 선점한 스레드가 자원의 사용을 마치고 lock.release()를 호출하여 풀어줬을 때 그제서야 사용할 수 있게된다.
# for using Lock method(acquire(), release())
from multiprocessing import Process, Lock

# for Put Lock objects into variables(lock)
lock = Lock()

PORT_NUMBER = 8666 #포트넘버 정의
g_txFileName = "txData.csv" #트랜잭션데이터 파일
g_bcFileName = "blockchain.csv" #블록체인 파일
g_nodelstFileName = "nodelst.csv" #여러 서버로 채굴을 할 때 인접 노드를 미리 등록해주는 것
g_receiveNewBlock = "/node/receiveNewBlock"
g_difficulty = 5 #난이도 정의
g_maximumTry = 100 #최대 시도 횟수
g_nodeList = {'127.0.0.1':'8668'}  #인접 노드를 하드코딩으로 정의 # trusted server list, should be checked manually


class Block: #블록 클래스 클래스 안에 작은 모듈들이 들어가게됨
    #init ->초기화 메서드 # 어떤 클래스의 객체가 만들어질 때 자동으로 호출되어 그 객체가 갖게될 여러가지 성질을 정의
    #이제 블록 객체를 만들 때는 인잇을 통해 정의한 파라미터들을 넘겨줘야한다.
    def __init__(self, index, previousHash, timestamp, data, currentHash, proof ): #인덱스, 이전해시값, 시간, 데이터, 현재해시값, 작업증명
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.data = data
        self.currentHash = currentHash
        self.proof = proof

    # 파이썬 객체를 제이슨 형식으로 파싱함 #default -> 값이 입력되지 않으면 디폴트값 자동 입 # 람다 -> 인자:표현식 함수와 비슷하다고 생각하면 됨 인풋값:식 #__dict__ -> a = b 라는 객체를 {a:b}로 변경
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class txData: #트랜잭션 데이터 클라스

    def __init__(self, commitYN, sender, amount, receiver, uuid): #커밋여부, 전송자, 전송량?, 수신자, 고유 식별자
        self.commitYN = commitYN
        self.sender = sender
        self.amount = amount
        self.receiver = receiver
        self.uuid =  uuid


def generateGenesisBlock(): #제너레이트 블록 생성 함수
    print("generateGenesisBlock is called") #호출하면 안내문 출력
    timestamp = time.time() #시간 가지고와 타임스탬프 변수에 저장
    print("time.time() => %f \n" % timestamp)
    tempHash = calculateHash(0, '0', timestamp, "Genesis Block", 0)  #해시계산 함수(시간정보, 제네시스 블록을 파라미터로 넣어줌)로 받아온 임시해시값을 tempHash변수에 넣어줌
    print(tempHash)
    return Block(0, '0', timestamp, "Genesis Block",  tempHash,0) # 위에서 받아온 해시값을 이용해 제네시스 블록을 생성. 0번째 블록이 생성되었다.

def calculateHash(index, previousHash, timestamp, data, proof): # 해시값 계산 함수 (새로 생성)
    value = str(index) + str(previousHash) + str(timestamp) + str(data) + str(proof) #받아온 파라미터들을 문자열로 변환해 모두 value 변수 안에 넣어줌
    sha = hashlib.sha256(value.encode('utf-8')) # 생성한 문자열을 해시 함수를 돌려 해시값 생성 후 리턴
    return str(sha.hexdigest())

def calculateHashForBlock(block): # 현재의 해시값에는 이전의 해시값들이 포함되어야한다. 그래서 파라미터로 전달받은 블록의 해시값을 계산한다.
    return calculateHash(block.index, block.previousHash, block.timestamp, block.data, block.proof)

def getLatestBlock(blockchain): # 블록체인의 가장 마지막 블록을 가지고 오는 함수
    return blockchain[len(blockchain) - 1] #블록체인의 길이 -1 -> 마지막 인덱스를 통해 가지고 온 뒤 리턴해준다.

def generateNextBlock(blockchain, blockData, timestamp, proof): #다음 블록 생성 함수 (전체블록체인, 블록데이터, 시간, 작업증명) #블록을 생성하기 위해선 더 많은 파라미터가 있어야하는데 갯수가 적다! 부족한 부분은 안에서 정의하자.
    previousBlock = getLatestBlock(blockchain) # 프리비어스 블록 = 위에서 정의한 함수를 호출해 가지고 온 블록체인의 마지막 블록
    nextIndex = int(previousBlock.index) + 1 # 현재 블록의 마지막 인덱스 +1 로 다음 블록의 인덱스를 지정해줌
    nextTimestamp = timestamp #nextTimestammp = 파라미터로 들어온 시간
    nextHash = calculateHash(nextIndex, previousBlock.currentHash, nextTimestamp, blockData, proof) #다음 해시값 = 파라미터가 다 준비되었으니 calculateHash함수를 호출하자! 그러면 리턴으로 해시값을 준다!
    # index, previousHash, timestamp, data, currentHash, proof
    return Block(nextIndex, previousBlock.currentHash, nextTimestamp, blockData, nextHash,proof) #generateNextBlock의 리턴으로 블록 객체 생성( 위에서 구한 인덱스, 마지막블록의 해시값, 인풋받은 시간, 블록데이타, 다음해시값(지금생성하는 블록의 해시값), 작업증명)


# 20190605 / (YuRim Kim, HaeRi Kim, JongSun Park, BohKuk Suh , HyeongSeob Lee, JinWoo Song)
# /* WriteBlockchain function Update */
# If the 'blockchain.csv' file is already open, make it inaccessible via lock.acquire()
# After executing the desired operation, changed to release the lock.(lock.release())
# Reason for time.sleep ():
# prevents server overload due to repeated error message output and gives 3 seconds of delay to allow time for other users to wait without opening file while editing and saving csv file.

def writeBlockchain(blockchain): #함수 외부에서 블록체인을 파라미터로 받아온다

    blockchainList = [] #빈 리스트 정의 ->블록체인 리스트는 밖에서 파라미터로 받아온 블록체인에대한 정보를 담아주는 변수이다.

    for block in blockchain: #외부에서 받아온 블록체인의 요소 하나씩 가지고오기

        blockList = [block.index, block.previousHash, str(block.timestamp), block.data, block.currentHash,block.proof ] #블록리스트라는 리스트 변수에 한 블록이 가지고 있는 정보들을 넣기
        blockchainList.append(blockList) #블록체인리스트 변수에 방금 생성한 블록 리스트 어팬드해주기. 블록체인리스트는 다중배열이 되어있을 것.

    #[STARAT] check current db(csv) if broadcasted block data has already been updated
    try: #파일 읽기 시도 / 블록체인 파일을 읽기모드로 읽어옴 밑에서부터는 file이라고 명명, #newline=''을 지정하지 않으면, 따옴표 처리된 필드에 포함된 줄 넘김 문자가 올바르게 해석되지 않 newline=''을 지정하는 것이 안전
        with open(g_bcFileName, 'r',  newline='') as file:
            blockReader = csv.reader(file) #블록체인리더(리스트) = csv형태인 블록체인 파일을 읽은 것(우리에게 저장되어있는 csv파일을 읽어온 것)
            last_line_number = row_count(g_bcFileName) #last_line_number = 블록체인의 행 수를 읽은 것 ( 0번째 블록을 포함 몇개의 블록이 존재하는지 알 수 있음 )
            for line in blockReader: #블록리더 (블록체인 파일)에서 한 줄씩을 가지고 옴 / 블록체인파일의 수가 마지막 행 숫자와 같아지면 (즉 , for 문의 마지막에 다다르면)
                if blockReader.line_num == last_line_number: # last블록 변수에 파일 마지막 줄의 블록정보 (#인덱스, 이전해시값, 시간, 데이터, 현재해시값, 작업증명)를 담아준다
                    lastBlock = Block(line[0], line[1], line[2], line[3], line[4], line[5])


        # 이 이프문은 여러 서버로 블록을 채굴할 경우에 생길 수 있는 예외를 정의했다. 만약 내가 블록을 채굴했다. 그리고 이제 그 정보를 csv파일에 저장하려고 한다. csv파일에 새로운 블록에 대한 정보를 쓰려면 새로운 인덱스가 필요하다.
        # 내가 채굴한 블록이 5번째 블록이라고 하자. 아직 나는 csv파일에 블록 정보를 쓰지 못했기때문에 파일의 마지막 인덱스는 4일것이다. 그러면 내가 쓸려는 5번째 인덱스를 csv파일에 쓰려면 4+1 인 5가 내가 작성하려는 인덱스의 정보가 될것이다.
        # 정상적인 경우라면 내가 채굴한 블록 (5번째)의 숫자와 내가 파일로 작성하려는 숫자(5번째를 채굴했다고 작성해야하니까) 는 같아야 할 것이다.
        # 그런데 만약 내가 작성하려는 인덱스와 내가 채굴한 블록의 숫자가 같지 않다면?? 누군가 나보다 먼저 블록을 채굴해서 이미 파일에 업로드를 해버린 것이다. 몇개를 업로드 했는지는 아직 알 수 없다. 그럼 내가 채굴한 블록은 더이상 사용하지 못할 것이다.
        # 그럴 때 우선 인덱스 시퀀스 미스매치 안내문을 출력한다.
            # 그런데 위의 조건을 만족하면서 동시에 '내가 채굴한 블록정보' 와 csv파일의 마지막 블록정보의 숫자가 같다면?
            # 누군가가 나와 간발의 차이로 똑같이 5번째 블록을 채굴했는데, 나보다 먼저 파일에 업로드를 해버린 것이다.
            # 나는 5번 블록을 채굴했는데, 누군가 파일에 5번 블록에 대한 정보를 업로드해버렸다.
            # 이런 경우 파일의 마지막 인덱스 == 내가 체굴한 블록 인덱스 인 것이다. 그런 경우 "블록체인이 이미 업데이트되었습니다" 출력에 하는 것 ( 조금 더 자세한 정보를 출력하기 위해서 )
        # 이런 예외에 걸린 경우 writeBlockChain함수는 더이상 의미가 없음으로 리턴값으로 함수에서 빠져나온다.
        if int(lastBlock.index) + 1 != int(blockchainList[-1][0]):
            print("index sequence mismatch")
            if int(lastBlock.index) == int(blockchainList[-1][0]):
                print("db(csv) has already been updated")
            return
    except: #파일을 읽는데 실패한 경우 안내문 출력한 후 패스
        print("file open error in check current db(csv) \n or maybe there's some other reason")
        pass
        #return
    # [END] check current db(csv)
    openFile = True #오픈 파일이라는 변수에 거짓 값을 넣어준다.
    while openFile: #오픈 파일이 참인 경우 반복문 실행
        if blockchainList != []: #블록체인리스트가 비어있지 않다면,
            try:#뭔가를 시도해보자
                lock.acquire()#락 선점을 시도했다.
                with open(g_bcFileName, "w", newline='') as file: #블록체인csv파일을 쓰기모드로 읽어온다.
                    writer = csv.writer(file) #파일 작석을 위한 변수에 할당
                    writer.writerows(blockchainList) #csv파일에 블록체인 리스트를 작성해준다.
                    blockchainList.clear() #블록체인 리스트 초기화 / 잘 작성되었다는 안내문구 출력
                    print("write ok")
                    openFile = False # 오픈 파일을 트루로 변경
                    for block in blockchain: #블록체인에 존재하는 행 하나하나를 가지고오기
                        updateTx(block) #트랜젝션을 업데이트 할 수 있는 함수 호출, 파라미터로 블록을 넣어준다.
                    print('Blockchain written to blockchain.csv.') #블록체인이 파일로 작성되었다는 안내문구 출력
                    print('Broadcasting new block to other nodes') #브로드캐스팅 하겠다는 것을 알려준다.
                    broadcastNewBlock(blockchain) #브로드캐스트 함수를 호출해 다른 노드들에게 브로드캐스트로 블록체인 채굴을 알린다
                    lock.release()  #자원의 점유를 풀어준다.
            except: #선점에 실패한 경우 혹은 파일을 여는데 실패한 경우 3초대기 후 실패에대한 안내문구 출력 한 뒤 자원 선점을 풀어준다
                    time.sleep(3) #선점에 실패할 수도 있는데 풀어주는 이유는, 에러가 난 경우에는 선점에 성공한건지 실패한건지 명확하게 알 수 없기 때문에 일단 풀어주는 것
                    print("writeBlockchain file open error")
                    lock.release()
        else: #블록체인 리스트가 비어있다면 비어있다는 안내문구 출력
            print("Blockchain is empty")

def readBlockchain(blockchainFilePath, mode = 'internal'): #블록체인파일 경로를 파라미터로 받아온다. 디폴트값 없기때문에 파라미터 들어와야함 / 모드는 디폴트값이 있어 호출시 없어도 가능. 여기서 모드는 내부 값을 가져오는 듯 하다.
    print("readBlockchain") #블록체인 읽어온다는 안내문구 출력 후 빈 배열을 하나 설정해준다.
    importedBlockchain = []

    try: #파일 읽어오기 시도 성공했을 경우
        with open(blockchainFilePath, 'r',  newline='') as file: #파일을 읽기 모드로 연다 new line이 개행문자 구분해줘서 라인바이라인으로 읽음 읽어서 file에 넣자.
            blockReader = csv.reader(file) #읽어온 파일을 블록리더 변수에 넣어준다. 여기서 블록리더의 타입은 리스트이다
            for line in blockReader: #포문을 돌며 읽어온 컬럼 하나하나를 블록으로 생성함.
                block = Block(line[0], line[1], line[2], line[3], line[4], line[5]) #블록이라는 변수 안에 읽어온 라인의 정보 (블록정보) 를 넣어준 뒤 블록리더(빈 배열에) 한줄씩 어팬드해준다.
                importedBlockchain.append(block) # [ ㅁ, ㅁ, ㅁ, ㅁ, ㅁ, ㅁ ]

        print("Pulling blockchain from csv...") #csv에서 블록체인을 땡겨온다.

        return importedBlockchain #완성된 배열을 리턴값으로 돌려준다. (이 배열에는 csv파일에 업로드 되어있는 모든 블록의 정보가 들어있을 것)

    except: #파일을 읽어오는 것을 실패했을 경우
        if mode == 'internal' : #모드가 인터널인 경우 -> 인터널 - 내부적으로 필요에 의해서 호출된거고 그 외에는 엘스문으로 들어감 보통은 위의 트라이 문에서 끝난다. (이라인은 보통 제네시스 블록을 호출할 때만 사용)
            blockchain = generateGenesisBlock() # 블록체인이라는 변수에 제네시스 블록 함수를 호출한다. (그럼 블록체인이라는 배열에는 0번째 제네시스 블록이 생성되어있는 상태일 것이다.)
            importedBlockchain.append(blockchain) #try문에 들어가지 못했기 때문에 지금 importBlockChain 은 빈 배열일 것이다. 그곳에 0번째 블록인 제네시스 블록을 넣어준다.
            writeBlockchain(importedBlockchain) #제네시스 블록이 들어가있는 importBlockChain 변수를 writeBlockChain 함수에 파라미터로 넣어준다. 만약 문제가 없다면 csv 파일로 작성될 수 있을 것이다.
            return importedBlockchain #임포트 블록체인 변수를 리턴값으로 반환해준다.
        else : #모드가 인터널이 아니라면, 리턴값은 아무것도 없다.
            return None

def updateTx(blockData) : #트랜잭션을 업데이트 해주는 함수 블록 데이터를 파라미터로 받는다.

    phrase = re.compile(r"\w+[-]\w+[-]\w+[-]\w+[-]\w+") #정규표현식 사용을 위해 re 라이브러리를 불러왔다. 식이 기니 변수에 넣어주 # [6b3b3c1e-858d-4e3b-b012-8faac98b49a8]UserID hwang sent 333 bitTokens to UserID kim.
    matchList = phrase.findall(blockData.data) #인풋값으로 받은 블록데이터.데이터 중에 정규표현식과 같은 형태의 데이터들을 모주 찾아온다. 찾아온 아이들을 매치리스트라는 변수에 넣어줌
    if len(matchList) == 0 : #만약 일치하는 값이 없어 matchList의 길이가 0이라면, 매치되는 것을 찾지 못했다는 안내 문구를 출력 (블록 데이터와 블록 인덱스를 함께 출력해줌) 후 함수 빠져나오기
        print ("No Match Found! " + str(blockData.data) + "block idx: " + str(blockData.index))
        return

    tempfile = NamedTemporaryFile(mode='w', newline='', delete=False) #tempfile = 임시파일 생성 모듈 호출 , 쓰기모드, 개행문자 구분, 자동삭제값 False

    with open(g_txFileName, 'r') as csvfile, tempfile: #트랜젝션 데이터 파일 열기 , 두개의 변수에 각각 담아준다. tempfile 은 임시파일이 변수에 담겨있는 상태이다.
        reader = csv.reader(csvfile) #트랜잭션 데이터를 읽어와 reader에 임시파일에 작성하는 부분은 writer변수에 담아준다.
        writer = csv.writer(tempfile)
        for row in reader: #일기파일에서 한 행씩 가지고 오기
            if row[4] in matchList: #만약 가지고 온 행 (블록) 의 4번째 정보가 매치리스트에 존재한다면, 행을 업데이트한다는 안내문구 출력 후 그 행의 0번째 정보를 1로 바꿔준다.
                print('updating row : ', row[4])
                row[0] = 1
            writer.writerow(row) #임시 파일에 그 행을 추가해줌

    shutil.move(tempfile.name, g_txFileName) #shutil라이브러리 - 파일 및 디렉토리 작업을 수행하는 라이브러리) -> 임시파일의 이름을
    csvfile.close() #두 파일 다 닫아주고 트랜잭션 데이터가 업데이트 됐음을 알린다.
    tempfile.close()
    print('txData updated')

# 20190605 /(YuRim Kim, HaeRi Kim, JongSun Park, BohKuk Suh , HyeongSeob Lee, JinWoo Song)
# /* writeTx function Update */
# If the 'txData.csv' file is already open, make it inaccessible via lock.acquire()
# After executing the desired operation, changed to release the lock.(lock.release())
# Reason for time.sleep ():
# prevents server overload due to repeated error message output and gives 3 seconds of delay to allow time for other users to wait without opening file while editing and saving csv file.
# Removed temp files to reduce memory usage and increase work efficiency.
def writeTx(txRawData): #트렌잭션을 작성하기위한 함수 정의. 호출 시 트랜젝션 데이터가 들어온다 (아마 새로운 트랜젝션의 데이터가 들어오는 듯 함)
    print(g_txFileName) #먼저 트랜잭션데이터 파일 이름을 출력해준다 / 빈 배열 두개를 설정
    txDataList = []
    txOriginalList = []
    for txDatum in txRawData: #파라미터로 받아온 새로운 트랜잭션데이터 요소를 한 행씩 꺼내온다. / txList 변수에 [꺼내온 한 행의 정보 (커밋여부, 송신자, 양, 수신자, 고유번호)] 를 담아준다.
        txList = [txDatum.commitYN, txDatum.sender, txDatum.amount, txDatum.receiver, txDatum.uuid]
        txDataList.append(txList) #가지고 온 정보들을 트랜잭션 데이터 리스트에 넣어준다.

    try: #트랜잭션 데이터 파일 열기 시도 / 파일을 읽어 reader변수에 넣어준다.
        with open(g_txFileName, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader: #읽어온 트랜잭션 데이터 파일을 한 행씩 가지고 온다.
                txOriginalList.append(row) #txOriginalList에 읽어온 트랜잭션 데이터의 행들을 추가해준다.

            openWriteTx = False #변수값을 false로 설정해준다.
            while not openWriteTx: #변수가 거짓일 때 while문 실행 / 스래드가 loc 선점 시도
                lock.acquire()
                try: #자원의 점유를 알리고 트랜젝션 데이터 파일을 열어준다. 이번에는 쓰기모드로 설정
                    print("NewTxData lock.acquire")
                    with open(g_txFileName, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        # adding new tx
                        writer.writerows(txOriginalList) #트랜잭션 데이터 파일에 행을 추가해준다 ( 읽어온 트랜잭션 데이터 파일 )
                        writer.writerows(txDataList) #트랜잭션 데이터 파일에 새로운 트랜잭션 정보를 추가해줌(우리가 이 함수 호출 시 파라미터로 받아온 값)
                        print("writeTx write ok")
                        csvfile.close() #파일 닫기
                        openWriteTx = True #변수 값을 트루로 바꿈 (이제 더이상 while문에 들어오지 않는다)
                        lock.release() #점유를 해제

                except Exception as e: #읽기성공 +쓰기 실패일 경우 이 except문으로 들어온다. 실패했을 경우 안내문구 출력 후 자원 점유 해제. (아래에서 다시 한 번 쓰기를 시도하게 됨)
                    print(e)
                    time.sleep(3)
                    print("file open error")
                    lock.release()
    except: #읽기모드에 실패했을 경우 다시 한번 파일을 쓰기모드로 여는 것을 시도해보고 새로운 트랜잭션 데이터를 행으로 작성해준다
        # this is 1st time of creating txFile
        try:
            with open(g_txFileName, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerows(txDataList)
        except: #읽기모드 실패 + 쓰기모드 실퍠 = 리턴값을 0으로
            return 0
    return 1 #아닌경우(읽기/쓰기 둘 다 성공한 경우) 리턴값은 1
    print('txData written to txData.csv.')

def readTx(txFilePath): #트랜잭션 데이터를 읽어오는 함수 정의. 안내문구 출력 후 빈 배열을 잡아준다.
    print("readTx")
    importedTx = []

    try: #파라미터로 들어온 파일을 읽기모드로 열기 시도
        with open(txFilePath, 'r',  newline='') as file:
            txReader = csv.reader(file)
            for row in txReader: #읽어온 파일을 한 행씩 가지고 온다
                if row[0] == '0': #읽어온 행의 맨 앞 요소가 0일 경우 -> 라인이라는변수에 txData 클래스를 호출하고 행의 정보들을 넣어준다.  # find unmined txData
                    line = txData(row[0],row[1],row[2],row[3],row[4])
                    importedTx.append(line) #변수에 담겨있는 txData 객체를 importedTx리스트에 넣어준다. 리스트에는 각 행의 0번째 요소가 0인 데이터들만 들어가 있게 됨
        print("Pulling txData from csv...") #안내문구 출력
        return importedTx #리턴값으로 맨 앞이 0인 데이터들이 담겨있는 리스트 반환.
    except: #파일 읽기에 실패했을 경우에는 그냥 빈 배열 리턴
        return []

def getTxData(): #트랜잭션데이터를 가지고 오는 함수 정의. 먼저 빈 배열을 정의해준다.
    strTxData = ''
    importedTx = readTx(g_txFileName) #트랜잭선 정보가 들어있는 파일을 읽어와 변수에 넣어준다.
    if len(importedTx) > 0 : #만약 트랜잭션 정보가 존재한다면?
        for i in importedTx: #그 정보를 하나씩 가지고 오자
            print(i.__dict__) # 정보를 딕셔너리 형태로 바꿔 출력해준다 /  아래의 transactin 문자열에 담겨있는 값은 현재 "[고유번호값] UserId 전송자 sent 전송량 bitTokens to userID 수신자."
            transaction = "["+ i.uuid + "] UserID " + i.sender + " sent " + i.amount + " bitTokens to UserID " + i.receiver + ". "
            print(transaction) #위의 정보를 담아둔 문자열 출력
            strTxData += transaction #위에 정의해둔 빈 문자열에 우리가 담아준 트랜잭션 정보 밀어넣기

    return strTxData #트랜잭션 정보를 담고있는 문자열을 리턴값으로 돌려줌

def mineNewBlock(difficulty=g_difficulty, blockchainPath=g_bcFileName): #파라미터 주지 않아도 여기서 설정한 디폴트값이 들어감/ 리드블록체인 함수 호출
    blockchain = readBlockchain(blockchainPath) # 블록체인 패스가 뭐야.. 할수도 있지만 잘 보면 위에서 디폴트 값으로 블록체인패스라는 변수 안에 블록체인 파일 명이 들어가있다. 결국 블록체인 파일 이름을 파라미터로 주고 함수를 호출한 것 정상적인 경우라면 readBlockChain 함수에서 리턴값으로 배열을 반환해주었을 것이다. 그 값을 변수에 담자
    strTxData = getTxData() #getTxData함수 실행 , 만약 정상적으로 실행이 됐다면 트랜잭션 정보를 담고있는 문자열을 리턴값으로 주었을 것이다.
    if strTxData == '' : #만약 그 변수 값이 빈 값이라면 (정상적으로 블록체인 파일을 읽어오지 못했다면) 트랜잭선 정ㅈ보를 찾지 못했다는 안내문구 출력 후 함수 탈출
        print('No TxData Found. Mining aborted')
        return

    timestamp = time.time() #트랜잭션 정보가 존재한다면(위의 if문에 걸리지 않는다면) 타임스탬프 변수에 현재 시간을 담아준다
    proof = 0 #작업증명 값 0으로 설정하고 newBlockFound 값은 false로 설정 / 블록을 채굴중이라는 안내문구 출력
    newBlockFound = True #변수값을 트루로 잡아주고 변수를 생성해준다.

    print('Mining a block...')

    while newBlockFound: #while문 진입 / newBlockAttempt 변수에 기존블럭에 이어서 새 블록을 만들 수 있는 함수를 호출해준다.
        newBlockAttempt = generateNextBlock(blockchain, strTxData, timestamp, proof) #(블록체인, 트랜잭션데이터, 시간, 작업증명 값을 파라미터로 넣어준다) 이렇게 넣어주면 이 함수에서는 부족한 파라미터를 생성해 (해시값 등) 6개의 파라미터를 채워 Block 클래스를 호출하고 파라미터 값이 블록에 저장됨으로서 새로운 블록이 탄생하게 될 것이다.
        if newBlockAttempt.currentHash[0:difficulty] == '0' * difficulty: #새 블록의 현재 해시값[인덱스 0부터: 난이도로 정의한 값(연속으로 0이 몇개가 나와한다는 값)] 이  "0" * 난이도의 개수와 같다면 (만약 같지 않다면 새 블록은 유효하지 않다)
            stopTime = time.time() #현재시간 변수 설정
            timer = stopTime - timestamp #타이머라는 변수에 현재시간 - 위에서 정의한 timeStamp 값을 빼준다.
            print('New block found with proof', proof, 'in', round(timer, 2), 'seconds.')
            newBlockFound = False #이제 while문에는 진입하지않는다
        else: #아닌경우에 작업증명 값에 1을 더해준다.
            proof += 1

    blockchain.append(newBlockAttempt) #블록체인에 새로 생성된 블록을 추가해줌
    writeBlockchain(blockchain) #writeBlockChain함수를 호출하고 블록체인을 파라미터로 넣어준다 ( 위에서 살펴본 것 처럼 내가 채굴한 블록이 누군가가 먼저 채굴하지 않았다면 csv파일에 업로드되고 성공적으로 채굴이 마무리 될 것이다)

def mine(): #이 함수를 호출하면 함수 내부에서 다시 mineNewBlock을 호출해준다.
    mineNewBlock()

def isSameBlock(block1, block2): #파라미터로 들어온 두개의 블록이 같은 블록인지 판별하는 함수 블록 두개의 값을 파라미터로 받아와 함수를 정의
    if str(block1.index) != str(block2.index): #두개의 인덱스 / 이전해시값 / 데이터 / 현재해시값 / 작업증명 값 중 하나라도 같지 않다면 False를 리턴
        return False
    elif str(block1.previousHash) != str(block2.previousHash):
        return False
    elif str(block1.timestamp) != str(block2.timestamp):
        return False
    elif str(block1.data) != str(block2.data):
        return False
    elif str(block1.currentHash) != str(block2.currentHash):
        return False
    elif str(block1.proof) != str(block2.proof):
        return False
    return True #위의 예시에 하나도 걸리지 않을 경우 ( 즉 두 블록이 모든 정보가 같은 블록일 경우 ) True 값을 리턴해준다.

def isValidNewBlock(newBlock, previousBlock): #블록이 유효한지 판단해주는 함수 ( 새 블록, 이전블록 ) 을 파라미터로 받는다
    if int(previousBlock.index) + 1 != int(newBlock.index): #이전블록의 인덱서 + 1이 새 블록의 값과 같지 않다면 ( 인덱스가 잘못되었다는 이야기!) 그렇다면 맞지 않다는 안내문구 출력
        print('Indices Do Not Match Up')
        return False #false값 반환
    elif previousBlock.currentHash != newBlock.previousHash: #이전 블록의 현재 해시값이 새블록의 과거 이전 해시값과 같지 않은 경우 ( 새 블록의 이전 해시 == 과거 블록의 현재 해시 ) 라는 공식이 성립해야 정상적인 블록이라고 할 수 있다.
        print("Previous hash does not match")
        return False #해시값이 일치하지 않는다는 안내문구 출력 후 거짓 리턴
    elif calculateHashForBlock(newBlock) != newBlock.currentHash: #calculateHashForBlock 함수에 파라미터로 새블록을 넣어준다. 거기서 나온 해시값이 새로운 블록의 현재 해시값과 다르다면 ? 이 또한 정상적인 블록이 아니다. 그렇다면 해시값이 유효하지 않다는 안내문구 출력.
        print("Hash is invalid")
        return False
    elif newBlock.currentHash[0:g_difficulty] != '0' * g_difficulty: #새 블록의 현재 해시값[인덱스 0부터: 난이도로 정의한 값(연속으로 0이 몇개가 나와한다는 값)] 이  "0" * 난이도의 개수와 같지 않다면 이것도 유효하지 않은 해시값이다. 해시 난이도가 적절하지 않다는 안내문구 출력
        print("Hash difficulty is invalid")
        return False
    return True

def newtx(txToMining):

    newtxData = []
    # transform given data to txData object
    for line in txToMining:
        tx = txData(0, line['sender'], line['amount'], line['receiver'], uuid.uuid4())
        newtxData.append(tx)

    # limitation check : max 5 tx
    if len(newtxData) > 5 :
        print('number of requested tx exceeds limitation')
        return -1

    if writeTx(newtxData) == 0:
        print("file write error on txData")
        return -2
    return 1

def isValidChain(bcToValidate):
    genesisBlock = []
    bcToValidateForBlock = []

    # Read GenesisBlock
    try:
        with open(g_bcFileName, 'r',  newline='') as file:
            blockReader = csv.reader(file)
            for line in blockReader:
                block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                genesisBlock.append(block)
#                break
    except:
        print("file open error in isValidChain")
        return False

    # transform given data to Block object
    for line in bcToValidate:
        # print(type(line))
        # index, previousHash, timestamp, data, currentHash, proof
        block = Block(line['index'], line['previousHash'], line['timestamp'], line['data'], line['currentHash'], line['proof'])
        bcToValidateForBlock.append(block)

    #if it fails to read block data  from db(csv)
    if not genesisBlock:
        print("fail to read genesisBlock")
        return False

    # compare the given data with genesisBlock
    if not isSameBlock(bcToValidateForBlock[0], genesisBlock[0]):
        print('Genesis Block Incorrect')
        return False

    # tempBlocks = [bcToValidateForBlock[0]]
    # for i in range(1, len(bcToValidateForBlock)):
    #    if isValidNewBlock(bcToValidateForBlock[i], tempBlocks[i - 1]):
    #        tempBlocks.append(bcToValidateForBlock[i])
    #    else:
    #        return False

    for i in range(0, len(bcToValidateForBlock)):
        if isSameBlock(genesisBlock[i], bcToValidateForBlock[i]) == False:
            return False

    return True

# 20190605 / (YuRim Kim, HaeRi Kim, JongSun Park, BohKuk Suh , HyeongSeob Lee, JinWoo Song)
# /* addNode function Update */
# If the 'nodeList.csv' file is already open, make it inaccessible via lock.acquire()
# After executing the desired operation, changed to release the lock.(lock.release())
# Reason for time.sleep ():
# prevents server overload due to repeated error message output and gives 3 seconds of delay to allow time for other users to wait without opening file while editing and saving csv file.
# Removed temp files to reduce memory usage and increase work efficiency.
def addNode(queryStr):
    # save
    previousList = []
    nodeList = []
    nodeList.append([queryStr[0],queryStr[1],0]) # ip, port, # of connection fail

    try:
        with open(g_nodelstFileName, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    if row[0] == queryStr[0] and row[1] == queryStr[1]:
                        print("requested node is already exists")
                        csvfile.close()
                        nodeList.clear()
                        return -1
                    else:
                        previousList.append(row)

            openFile3 = False
            while not openFile3:
                lock.acquire()
                try:
                    with open(g_nodelstFileName, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(nodeList)
                        writer.writerows(previousList)
                        csvfile.close()
                        nodeList.clear()
                        lock.release()
                        print('new node written to nodelist.csv.')
                        return 1
                except Exception as ex:
                    print(ex)
                    time.sleep(3)
                    print("file open error")
                    lock.release()

    except:
        # this is 1st time of creating node list
        try:
            with open(g_nodelstFileName, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerows(nodeList)
                nodeList.clear()
                print('new node written to nodelist.csv.')
                return 1
        except Exception as ex:
            print(ex)
            return 0

def readNodes(filePath):
    print("read Nodes")
    importedNodes = []

    try:
        with open(filePath, 'r',  newline='') as file:
            txReader = csv.reader(file)
            for row in txReader:
                line = [row[0],row[1]]
                importedNodes.append(line)
        print("Pulling txData from csv...")
        return importedNodes
    except:
        return []

def broadcastNewBlock(blockchain):
    #newBlock  = getLatestBlock(blockchain) # get the latest block
    importedNodes = readNodes(g_nodelstFileName) # get server node ip and port
    reqHeader = {'Content-Type': 'application/json; charset=utf-8'}
    reqBody = []
    for i in blockchain:
        reqBody.append(i.__dict__)

    if len(importedNodes) > 0 :
        for node in importedNodes:
            try:
                URL = "http://" + node[0] + ":" + node[1] + g_receiveNewBlock  # http://ip:port/node/receiveNewBlock
                res = requests.post(URL, headers=reqHeader, data=json.dumps(reqBody))
                if res.status_code == 200:
                    print(URL + " sent ok.")
                    print("Response Message " + res.text)
                else:
                    print(URL + " responding error " + res.status_code)
            except:
                print(URL + " is not responding.")
                # write responding results
                tempfile = NamedTemporaryFile(mode='w', newline='', delete=False)
                try:
                    with open(g_nodelstFileName, 'r', newline='') as csvfile, tempfile:
                        reader = csv.reader(csvfile)
                        writer = csv.writer(tempfile)
                        for row in reader:
                            if row:
                                if row[0] == node[0] and row[1] ==node[1]:
                                    print("connection failed "+row[0]+":"+row[1]+", number of fail "+row[2])
                                    tmp = row[2]
                                    # too much fail, delete node
                                    if int(tmp) > g_maximumTry:
                                        print(row[0]+":"+row[1]+" deleted from node list because of exceeding the request limit")
                                    else:
                                        row[2] = int(tmp) + 1
                                        writer.writerow(row)
                                else:
                                    writer.writerow(row)
                    shutil.move(tempfile.name, g_nodelstFileName)
                    csvfile.close()
                    tempfile.close()
                except:
                    print("caught exception while updating node list")

def row_count(filename):
    try:
        with open(filename) as in_file:
            return sum(1 for _ in in_file)
    except:
        return 0

def compareMerge(bcDict):

    heldBlock = []
    bcToValidateForBlock = []

    # Read GenesisBlock
    try:
        with open(g_bcFileName, 'r',  newline='') as file:
            blockReader = csv.reader(file)
            #last_line_number = row_count(g_bcFileName)
            for line in blockReader:
                block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                heldBlock.append(block)
                #if blockReader.line_num == 1:
                #    block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                #    heldBlock.append(block)
                #elif blockReader.line_num == last_line_number:
                #    block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                #    heldBlock.append(block)

    except:
        print("file open error in compareMerge or No database exists")
        print("call initSvr if this server has just installed")
        return -1

    #if it fails to read block data  from db(csv)
    if len(heldBlock) == 0 :
        print("fail to read")
        return -2

    # transform given data to Block object
    for line in bcDict:
        # print(type(line))
        # index, previousHash, timestamp, data, currentHash, proof
        block = Block(line['index'], line['previousHash'], line['timestamp'], line['data'], line['currentHash'], line['proof'])
        bcToValidateForBlock.append(block)

    # compare the given data with genesisBlock
    if not isSameBlock(bcToValidateForBlock[0], heldBlock[0]):
        print('Genesis Block Incorrect')
        return -1

    # check if broadcasted new block,1 ahead than > last held block

    if isValidNewBlock(bcToValidateForBlock[-1],heldBlock[-1]) == False:

        # latest block == broadcasted last block
        if isSameBlock(heldBlock[-1], bcToValidateForBlock[-1]) == True:
            print('latest block == broadcasted last block, already updated')
            return 2
        # select longest chain
        elif len(bcToValidateForBlock) > len(heldBlock):
            # validation
            if isSameBlock(heldBlock[0],bcToValidateForBlock[0]) == False:
                    print("Block Information Incorrect #1")
                    return -1
            tempBlocks = [bcToValidateForBlock[0]]
            for i in range(1, len(bcToValidateForBlock)):
                if isValidNewBlock(bcToValidateForBlock[i], tempBlocks[i - 1]):
                    tempBlocks.append(bcToValidateForBlock[i])
                else:
                    return -1
            # [START] save it to csv
            # 20190605 / (kyuin Park, jiweon Lim, sunghoon Oh, sol Han )
            # TODO: append 정상여부 검증 필요
            blockchainList = []
            lengthGap = len(bcToValidateForBlock) - len(heldBlock)  # 받을 블록과 내 블록의 길이 차이
            for block in bcToValidateForBlock[-lengthGap:]:
                blockList = [block.index, block.previousHash, str(block.timestamp), block.data,
                             block.currentHash, block.proof]
                blockchainList.append(blockList)  # blockchainList에 타노드의 block을 list 형태로 담아줌
            with open(g_bcFileName, "a", newline='') as file:
                writer = csv.writer(file)
                writer.writerows(blockchainList)

            # [END] save it to csv
            return 1
        elif len(bcToValidateForBlock) < len(heldBlock):
            # validation
            #for i in range(0,len(bcToValidateForBlock)):
            #    if isSameBlock(heldBlock[i], bcToValidateForBlock[i]) == False:
            #        print("Block Information Incorrect #1")
            #        return -1
            tempBlocks = [bcToValidateForBlock[0]]
            for i in range(1, len(bcToValidateForBlock)):
                if isValidNewBlock(bcToValidateForBlock[i], tempBlocks[i - 1]):
                    tempBlocks.append(bcToValidateForBlock[i])
                else:
                    return -1
            print("We have a longer chain")
            return 3
        else:
            print("Block Information Incorrect #2")
            return -1
    else: # very normal case (ex> we have index 100 and receive index 101 ...)
        tempBlocks = [bcToValidateForBlock[0]]
        for i in range(1, len(bcToValidateForBlock)):
            if isValidNewBlock(bcToValidateForBlock[i], tempBlocks[i - 1]):
                tempBlocks.append(bcToValidateForBlock[i])
            else:
                print("Block Information Incorrect #2 "+tempBlocks.__dict__)
                return -1

        print("new block good")

        # validation
        for i in range(0, len(heldBlock)):
            if isSameBlock(heldBlock[i], bcToValidateForBlock[i]) == False:
                print("Block Information Incorrect #1")
                return -1
        # [START] save it to csv
        blockchainList = []
        for block in bcToValidateForBlock:
            blockList = [block.index, block.previousHash, str(block.timestamp), block.data, block.currentHash, block.proof]
            blockchainList.append(blockList)
        with open(g_bcFileName, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(blockchainList)
        # [END] save it to csv
        return 1

def initSvr():
    print("init Server")
    # 1. check if we have a node list file
    last_line_number = row_count(g_nodelstFileName)
    # if we don't have, let's request node list
    if last_line_number == 0:
        # get nodes...
        for key, value in g_nodeList.items():
            URL = 'http://'+key+':'+value+'/node/getNode'
            try:
                res = requests.get(URL)
            except requests.exceptions.ConnectionError:
                continue
            if res.status_code == 200 :
                print(res.text)
                tmpNodeLists = json.loads(res.text)
                for node in tmpNodeLists:
                    addNode(node)

    # 2. check if we have a blockchain data file
    last_line_number = row_count(g_bcFileName)
    blockchainList=[]
    if last_line_number == 0:
        # get Block Data...
        for key, value in g_nodeList.items():
            URL = 'http://'+key+':'+value+'/block/getBlockData'
            try:
                res = requests.get(URL)
            except requests.exceptions.ConnectionError:
                continue
            if res.status_code == 200 :
                print(res.text)
                tmpbcData = json.loads(res.text)
                for line in tmpbcData:
                    # print(type(line))
                    # index, previousHash, timestamp, data, currentHash, proof
                    block = [line['index'], line['previousHash'], line['timestamp'], line['data'],line['currentHash'], line['proof']]
                    blockchainList.append(block)
                try:
                    with open(g_bcFileName, "w", newline='') as file:
                        writer = csv.writer(file)
                        writer.writerows(blockchainList)
                except Exception as e:
                    print("file write error in initSvr() "+e)

    return 1

# This class will handle any incoming request from
# a browser
class myHandler(BaseHTTPRequestHandler):

    #def __init__(self, request, client_address, server):
    #    BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    # Handler for the GET requests
    def do_GET(self):
        data = []  # response json data
        if None != re.search('/block/*', self.path):
            if None != re.search('/block/getBlockData', self.path):
               # 20190605 / (kyuin Park, jiweon Lim, sunghoon Oh, sol Han )
               # TODO : http://localhost:8666/block/getBlockData?from=1&end=10 -> from, end 문자열 검사

                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    block = readBlockchain(g_bcFileName, mode = 'external')
                    # 스마트금융 4기 김하나 미래산업기술동향 과제
                    # 총 6개의 예외를 정의해보았습니다.
                    # 1. 블록이 생성되지 않은경우
                    # 2. 쿼리문에 숫자가 아닌 문자가 들어온 경우
                    # 3. startpoint에 음수가 들어온 경우
                    # 4. startPoint가 블록의 길이보다 큰 경우
                    # 5. endPoint 값이 블록의 길이보다 길거나, 0보다 작을경우.
                    # 6. 한번에 조회하는 숫자가 100개보다 많을경우.

                    # 예외 1 : 블록이 생성되지 않았을 경우.
                    # 해결 1 : 블록이 존재하지 않는다는 안내문구 출력.
                    if block == None:
                        print("블록이 존재하지 않습니다.")
                        data.append("블록이 존재하지 않습니다.")
                    else:
                        # 예외 2 : 쿼리에 숫자가 아닌 문자가 들어온 경우
                        # 해결 2 : 일단 쿼리 형식이 올바른지 확인하기위해 int 형식으로 변환을 시도. 형식이 올바르지 않다면 except문으로 들어감.
                        try:
                            queryString = urlparse(self.path).query.split('&')
                            startPoint = int(queryString[0].split('=')[1]) - 1
                            endPoint = int(queryString[1].split('=')[1])

                            # 예외 3 : startPoint에 음수가 들어온 경우.
                            # 해결 3 : startPoint를 0으로 덮어씀.
                            if startPoint < 0  :
                                startPoint = 0

                            # 예외 4. startPoint가 블록의 길이보다 긴 경우
                            # 해결 4. 사용자에게 안내문구 출력 후 startPoint를 마지막 인덱스로 변경 (블록의 길이보다 더 큰 값을 넣었으니 넣을 수 있는 값중 가장 큰 값으로 바꿔줌)
                            if startPoint > len(block):
                                print("시작점이 잘못되었습니다. 설정할 수 있는 startPoint의 최대 범위는 {} 입니다. {} 번째 결과부터 조회합니다.".format((len(block) -1 ),(len(block) -1 )))
                                data.append("시작점이 잘못되었습니다. 설정할 수 있는 startPoint의 최대 범위는 {} 입니다. {} 번째 결과부터 조회합니다.".format((len(block) -1 ),(len(block) -1 )))
                                startPoint = len(block) -1

                            # 예외 5 : endPoint 값이 블록의 길이보다 길거나 0보다 작을경우.
                            # 아래에서 정의한 100이 넘어가는 예외 발생시 무조건 블록의 길이를 넘어가는 문제를 해결하기위해 블록의 길이보다 길고 endPoint - startPoint 가 100보다 작은 경우로 조건문을 작성했습니다.
                            # 해결 5-1 : 사용자에게 블록의 길이 알려줌.
                            # 해결 5 -2 : endPoint를 블록의 길이로 바꿔준다.
                            if (endPoint > len(block) and (endPoint - startPoint) < 100) or endPoint <= 0:
                                print("블록의 범위를 초과한 요청입니다. {} 개의 블록이 존재합니다.".format(len(block)))
                                data.append("블록의 범위를 초과한 요청입니다. {} 개의 블록이 존재합니다.".format(len(block)))
                                endPoint = len(block)

                            # 예외 6 : 한번에 조회하는 숫자가 100개보다 많을경우.
                            # 해결 6 : 리스트 분할 출력을 위한 for문
                            if (endPoint - startPoint) >= 100 : # 리스트 분할 출력을 위한 for문
                                start = startPoint # 인덱스 시작값을 startPoint로 잡아줌.
                                end = endPoint #인덱스의 마지막값을 endPoint로 잡아줌.
                                augmenter = 10 #한번에 출력할 값 정의 (여기서느 10으로 설정)
                                for i in range(start, end, augmenter):
                                    index = start + augmenter # 시작값 + 한번에 출력할 값
                                    printList = block[start:index] # 정의한 인덱스로 출력 범위 설정해 변수에 넣어줌
                                    if printList != []: # printList가 빈 리스트가 아니라면 if문 수행
                                        for element in printList: # printList의 element 하나씩 출력
                                            print(element.__dict__)
                                            data.append(element.__dict__)  # data에 element append
                                        start = index # 시작값을 마지막 인덱스 값으로 바꿔줌
                                        userInput = input("출력을 멈추시려면 엔터키를, 계속 출력을 원하시면 아무키나 입력하세요. ") # 사용자에게 계속 출력할지 선택. 사용자의 제약을 줄이기 위해 특정 문자가 아닌 아무 문자나 입력할 수 있게 처리.
                                        if len(userInput) > 0: # 사용자가 한글자라도 입력했다면 계속 수행
                                            continue
                                        else: # 아무것도 입력하지 않았으면 안내문구 출력 후 종료
                                            break
                                print("출력이 완료되었습니다.") #for 문이 끝나거나 break가 걸리면 안내문구 출

                            else : #출력해할 범위가 100보다 작은경우, 최종 startPoint와 endPoint를 이용해 for문.
                                for i in range(startPoint, endPoint):
                                    print(block[i].__dict__)
                                    data.append(block[i].__dict__)

                        except: #에외 1 해결 부분
                            print("잘못된 쿼리 형식입니다.")
                            data.append("잘못된 쿼리 형식입니다.")

                except:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    data.append("error")
                finally:
                    print("결과를 반환합니다.") #포스트맨으로 보내기 전 안내문구가 있으면 좋을 것 같아 추가해보았습니다.
                    self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

            elif None != re.search('/block/generateBlock', self.path):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                t = threading.Thread(target=mine)
                t.start()
                data.append("{mining is underway:check later by calling /block/getBlockData}")
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                data.append("{info:no such api}")
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

        elif None != re.search('/node/*', self.path):

            if None != re.search('/node/addNode', self.path):
                queryStr = urlparse(self.path).query.split(':')
                print("client ip : "+self.client_address[0]+" query ip : "+queryStr[0])
                if self.client_address[0] != queryStr[0]:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    data.append("your ip address doesn't match with the requested parameter")
                else:
                    try:
                        res = addNode(queryStr)
                    except:
                        pass
                    finally:
                        if res == 1:
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            importedNodes = readNodes(g_nodelstFileName)
                            data =importedNodes
                            print("node added okay")
                        elif res == 0 :
                            self.send_response(500)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            data.append("caught exception while saving")
                        elif res == -1 :
                            self.send_response(500)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            importedNodes = readNodes(g_nodelstFileName)
                            data = importedNodes
                            data.append("requested node is already exists")
                        self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

            elif None != re.search('/node/getNode', self.path):
                try:
                    importedNodes = readNodes(g_nodelstFileName)
                    data = importedNodes
                except:
                    data.append("error")
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                finally:
                    self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

        else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()


        # ref : https://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/

    def do_POST(self):

        if None != re.search('/block/*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if None != re.search('/block/validateBlock/*', self.path):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                #print(ctype) #print(pdict)

                if ctype == 'application/json':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    receivedData = post_data.decode('utf-8')
                    print(type(receivedData))
                    tempDict = json.loads(receivedData)  # load your str into a list #print(type(tempDict))
                    if isValidChain(tempDict) == True :
                        tempDict.append("validationResult:normal")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    else :
                        tempDict.append("validationResult:abnormal")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
            elif None != re.search('/block/newtx', self.path):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                if ctype == 'application/json':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    receivedData = post_data.decode('utf-8')
                    print(type(receivedData))
                    tempDict = json.loads(receivedData)
                    res = newtx(tempDict)
                    if  res == 1 :
                        tempDict.append("accepted : it will be mined later")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    elif res == -1 :
                        tempDict.append("declined : number of request txData exceeds limitation")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    elif res == -2 :
                        tempDict.append("declined : error on data read or write")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    else :
                        tempDict.append("error : requested data is abnormal")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))

        elif None != re.search('/node/*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if None != re.search(g_receiveNewBlock, self.path): # /node/receiveNewBlock
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                receivedData = post_data.decode('utf-8')
                tempDict = json.loads(receivedData)  # load your str into a list
                print(tempDict)
                res = compareMerge(tempDict)
                if res == -1: # internal error
                    tempDict.append("internal server error")
                elif res == -2 : # block chain info incorrect
                    tempDict.append("block chain info incorrect")
                elif res == 1: #normal
                    tempDict.append("accepted")
                elif res == 2: # identical
                    tempDict.append("already updated")
                elif res == 3: # we have a longer chain
                    tempDict.append("we have a longer chain")
                self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

try:

    # Create a web server and define the handler to manage the
    # incoming request
    # server = HTTPServer(('', PORT_NUMBER), myHandler)
    server = ThreadedHTTPServer(('', PORT_NUMBER), myHandler)
    print('Started httpserver on port ', PORT_NUMBER)

    initSvr()
    # Wait forever for incoming http requests
    server.serve_forever()

except (KeyboardInterrupt, Exception) as e:
    print('^C received, shutting down the web server')
    print(e)
    server.socket.close()
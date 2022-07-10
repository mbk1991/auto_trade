import win32com.client
import time
import pywinauto
import dashin_auto
import sys
from datetime import datetime

# 해당 기법은 급등 후 눌리는 음봉에서 매매를하는 방법임. 매수1호가 매수 , 매수 타이머는 사용하지 않는다.
# 수정할 것
# 매도시 fok 취소가 난 경우 조치
# 전체적인 코드 정리


# 크레온 플러스 실행
dashin_auto.auto_open()
print('크레온플러스 실행중입니다.')
# 크레온 플러스 실행 대기
time.sleep(60)


# 대신 API 인스턴스 바인딩
instCpCybos = win32com.client.Dispatch('CpUtil.CpCybos')  #사이보스플러스 연결 상태를 확인하는 인스턴스
instStockChart = win32com.client.Dispatch("CpSysDib.StockChart")  #차트데이터를 수신하는 인스턴스
instCpStockCode = win32com.client.Dispatch("CpUtil.CpStockCode")  #주식 종목명 및 코드를 조회하는 인스턴스
instCpCodeMgr = win32com.client.Dispatch(("CpUtil.CpCodeMgr"))  #각종 코드정보 및 코드리스트를 얻는 인스턴스
instMarketEye = win32com.client.Dispatch("CpSysDib.MarketEye")  # 여러종목의 필요항목을 한번에 수신하는 인스턴스
instCpTdUtil = win32com.client.Dispatch("CpTrade.CpTdUtil")  # 계좌정보
instCpTd0311 = win32com.client.Dispatch("CpTrade.CpTd0311")  # 매수 매도 주문 인스턴스
instCpTdNew5331A = win32com.client.Dispatch("CpTrade.CpTdNew5331A")  # 계좌별 매수 가능 금액/ 수량 데이터
instCpTdNew5331B = win32com.client.Dispatch("CpTrade.CpTdNew5331B")  # 계좌별 매도 가능 수량데이터
instCpTd6033 = win32com.client.Dispatch("CpTrade.CpTd6033")  # 계좌별 잔고 및 주문체결 평가현황데이터를 요청하고 수신한다
instStockMst = win32com.client.Dispatch("Dscbo1.StockMst")  # 현재가, 호가 관련
instCpConclusion = win32com.client.Dispatch("Dscbo1.CpCOnclusion")  # 주식 체결 실시간

# 계좌정보
instCpTdUtil.TradeInit()
accountNumber = instCpTdUtil.AccountNumber[0]  # 계좌번호
accFlag = instCpTdUtil.GoodsList(accountNumber,1)  #거래구분 코드

# 시간 정보
#프린트용 &파일명
date = datetime.now().strftime('%D')
timenow = datetime.now().strftime('%H:%M')
filedate = str(datetime.now().year)+'_'+str(datetime.now().month)+'_'+str(datetime.now().day)
filedate_yday = str(datetime.now().year)+'_'+str(datetime.now().month)+'_'+str(datetime.now().day-1)

#시간계산용
now = int(datetime.now().strftime('%H%M'))

# 연결 확인
def connect_check():
    print('사이보스플러스 연결를 체크합니다. 주인님')
    bConnect = instCpCybos.IsConnect
    if (bConnect == 0):
        print("PLUS가 정상적으로 연결되지 않았습니다요. ")
        exit() # 프로그램 종료
    elif (bConnect == 1):
        print('접속 성공입니다요. 주인님')


#거래기록 저장용 프린트
def printsave(*a):
    file = open('c:\\users\\administrator\\desktop\\auto_trade\\trade_record2.txt','a')
    print(*a)
    print(*a,file=file)
    file.close()

#타겟종목명 날짜별 저장용 프린트
def printsavetargetname(*a):
    file = open('c:\\users\\administrator\\desktop\\auto_trade\\target_list\\%s_targetname.txt'%filedate,'a')
    print(*a)
    print(*a,file=file)
    file.close()

#타겟종목 코드 날짜별 저장용 프린트  // 타겟리스트는 당일과 전일 날짜의 타겟종목 파일을 target_list로 바인딩함. 주말이나 공휴일을 끼면 어떻게 할 지 고민. 일단은 수동으로 파일을 수정한다.
def printsavetarget(*a):
    file = open('c:\\users\\administrator\\desktop\\auto_trade\\target_list\\target_list_total.txt','a')
    print(*a)
    print(*a,file=file)
    file.close()


#타겟종목 저장 1531 이후 실행/ 2to11 평균거래량 대비 0봉 거래량이 10배이상 또는 0봉거래량이 1000만 이상  /  1봉양봉,0봉음봉/ 0봉거래량 1봉대비 25%/ 60일최저가 대비 현재가가 200%미만/
def targetsavetxt():

    kospilist = instCpCodeMgr.GetStockListByMarket(1)  # 코스피 코드리스트
    kosdaqlist = instCpCodeMgr.GetStockListByMarket(2)  # 코스닥 코드리스트
    market = kospilist + kosdaqlist  # 코스피 + 코스닥 코드리스트
    market_stock = []
    for code in market:  # 주권 종목만 추출
        check = instCpCodeMgr.GetStockSectionKind(code)
        if check == 1:
            market_stock.append(code)

    for j,code in enumerate(market_stock):

       try:
        time.sleep(0.25)
        instStockChart.SetInputValue(0, code)  # 종목 코드
        instStockChart.SetInputValue(1, ord('2'))  # '1' 날짜구간 , '2' 갯수
        instStockChart.SetInputValue(4, 60)  # 3개 값 수신 요청  0봉(현재봉) ~ 10봉 까지 11개 값
        instStockChart.SetInputValue(5, [2,3,4,5,8])  # 시가0,고가1,저가2,종가3,거래량4
        instStockChart.SetInputValue(6, ord('D'))  # 일봉
        instStockChart.SetInputValue(9, ord('1'))  # 수정주가
        instStockChart.BlockRequest()  # 입력값을 api 요청

        codename = instCpStockCode.CodeToName(code)


        # 11일 거래량 모음 / 0봉제외 10봉 평균 거래량을 구하고자 함.
        volumes = []

        for i in range(11):
            volume = instStockChart.GetDataValue(4,i)
            volumes.append(volume)
        averagevolume_1to10 = (sum(volumes)-volumes[0]) / 10


        # 60일 종가 모음 / 60일 중 최저 종가와 현재가를 비교하고자 함
        lowprices = []

        for k in range(60):
            lowprice = instStockChart.GetDataValue(2,k)
            lowprices.append(lowprice)

        low_60 = min(lowprices)



        start_0 = instStockChart.GetDataValue(0,0)
        end_0 = instStockChart.GetDataValue(3,0)
        volume_0 = instStockChart.GetDataValue(4,0)
        gap_0 = end_0 - start_0

        start_1 = instStockChart.GetDataValue(0, 1)
        end_1 = instStockChart.GetDataValue(3, 1)
        volume_1 = instStockChart.GetDataValue(4, 1)
        gap_1 = end_1 - start_1
        rise_60 = round((end_0 / low_60), 2) * 100
       except:
            continue


       print(codename, j, '/', len(market_stock))


        #1봉은 2to11 평균 거래량 대비 1000% 이상 또는 1000만 거래량 이상

       if ((volume_0 > (volume_1*3))and((volume_0 > (averagevolume_1to10 * 10))\
                                        or (volume_0 > 10000000))) and (gap_0 > 0) and (rise_60 < 180):
            #if (volume_0 < (volume_1 * 0.25)) and (gap_0 < 0):
                print("타겟종목입니다요:",codename)
                printsavetarget(code)
                printsavetargetname((codename))



# 저장된 target_list.txt 를 읽어오는 함수// 0day, 1day 파일을 target_list로 바인딩
def target_list_read_txt():
    target_list_b = []
    f = open('C:\\Users\\Administrator\\Desktop\\auto_trade\\target_list\\target_list_total.txt', 'rt')
   # ff = open('C:\\Users\\Administrator\\Desktop\\auto_trade\\target_list\\%s_target_gg.txt' % filedate_yday, 'rt')
    target_list_a = f.readlines()
   # target_list_c = ff.readlines()
    for i in target_list_a:
        a = i.split('\n')[0]
        target_list_b.append(a)

    #for j in target_list_c:
     #   aa = j.split('\n')[0]
      #  target_list_b.append(aa)



    target_list = list(set(target_list_b))  # 중복값을 제거
    return target_list


# 보유종목 반환 함수
def bought_item():  # 보유종목 정보를 반환하는 함수  -> 종목보유여부 체크 및 매도 감시 시 활용
    instCpTdNew5331B.SetInputValue(0,accountNumber)
    instCpTdNew5331B.SetInputValue(1,accFlag[0])
    instCpTdNew5331B.SetInputValue(3,ord('1'))
    instCpTdNew5331B.SetInputValue(4,ord('1'))
    instCpTdNew5331B.BlockRequest()

    try:
        savestock_code = instCpTdNew5331B.GetDataValue(0,0)  # 보유종목 코드
        savestock_name = instCpTdNew5331B.GetDataValue(1,0)  # 보유종목 이름
        savestock_quant = instCpTdNew5331B.GetDataValue(12,0) #보유종목 매도 가능 수량
        return (savestock_name,savestock_quant,savestock_code)
    except:
        savestock_code = 'none'
        savestock_name = 'none'
        savestock_quant = 0
        return (savestock_name,savestock_quant,savestock_code)

# 보유종목이 있는지 체크하는 함수
def bought_check():
    instCpTdNew5331B.SetInputValue(0, accountNumber)
    instCpTdNew5331B.SetInputValue(1, accFlag[0])
    instCpTdNew5331B.SetInputValue(3, ord('1'))
    instCpTdNew5331B.SetInputValue(4, ord('1'))
    instCpTdNew5331B.BlockRequest()

    try:
        balance = instCpTdNew5331B.GetDataValue(12, 0)  # 매도가능수량
        if balance != 0:
            return 1  #매도가능 수량이 있음
    except:
        return 0  #매도가능 수량이 없음 / 없으면 에러가 남


# 매수조건/ 현재가와 5일선의 이격도 99~102 / 0일 거래량이 10거래일 최대 거래량 대비 25% 이하/
def buy_observer(instStockChart,target_list):  # target_list를 서치하여 1개의 종목을 찾아냄
    check = 0
    now = int(datetime.now().strftime('%H%M'))
    will_buy_item = []


    while (now > 900) and (now < 1500):
        now =int(datetime.now().strftime('%H%M'))
        timesleep(10)
        print(now,"매수 탐색은 15시부터 합니다요.")

    # 딕쇼나리를 만들어서 종목과 지표를 저장하고 for문이 한바퀴 돌았을때 len이 1이상이라면 그 중 가장 나은 조건을 매수
    while check == 0:
        for code in target_list:   # tqrget_list의 종목 별 0~11봉 거래량 값을 입력값으로 설정
            instStockChart.SetInputValue(0, code)   #종목 코드
            instStockChart.SetInputValue(1, ord('2'))   #'1' 날짜구간 , '2' 갯수
            instStockChart.SetInputValue(4, 11) # 5개 값 수신 요청  0봉(현재봉) ~ 10봉 까지 11개 값
            instStockChart.SetInputValue(5, [2,5,8])    # 시가,종가,거래량
            instStockChart.SetInputValue(6, ord('D'))   # 일봉
            instStockChart.SetInputValue(9, ord('1'))   # 수정주가
            instStockChart.BlockRequest()   #입력값을 api 요청
            time.sleep(0.25)

            codename = instCpStockCode.CodeToName(code)

            volumes = []
            for j in range(5):
                volume = instStockChart.GetDataValue(2,j+1)
                volumes.append(volume)
            maxvolume_5 = max(volumes)    # 1to11봉 사이 최대 거래량

            if (maxvolume_5 < 1000000):  # 5일 사이 최대 거래량이 100만보다 작다면 제외시킨다.
                target_list.remove(code)
                printsave(code,codename,"종목은 삭제해야합니다요.")
                continue

            # 5일평균선: 0to4 종가의 평균
            end_5 = []
            for i in range(5):
                end = instStockChart.GetDataValue(1,i)
                end_5.append(end)
            averageline_5 = sum(end_5) / 5    # 5일 평균값

            start_0 = instStockChart.GetDataValue(0,0)
            end_0 = instStockChart.GetDataValue(1,0)
            volume_0 = instStockChart.GetDataValue(2,0)
            gap = end_0 - start_0    # 양봉 여부 확인

            #5일평균 이격도
            aver5_gap = round(end_0 / averageline_5,2) * 100

            # 음봉 / 5일선 이격도 99~102 / 10일내 최대 거래량 대비 25%
            print("종목:",codename,"5일이격도:",aver5_gap,"gap:",gap,"5일최대거래량 비교:",(volume_0 < (maxvolume_5*0.25)))
            
            #이격도를 변수에 바인딩하고 해당 변수는 상승장, 하락장 조건에 따라 변동되도록 설정하는 방법도 있겠다
            if (gap<0) and (aver5_gap<=98) and (volume_0 < (maxvolume_5*0.25)):


                will_buy_item.append(code)
                dateprint = '[' + datetime.now().strftime('%D') + ' ' + datetime.now().strftime('%H:%M') + ']'
                printsave(dateprint,'종목을 찾았습니다요. 주인님. 종목명은',codename,'입니다요')
                check = 1   # while 문 탈출
                break

            if now > 1531:
                print('장이 종료되었습니다.')
                check = 1
                break
    return will_buy_item


# will_buy_item 호가 출력 및 반환 함수
def item_hoga_data(will_buy_item):   # 호가 정보를 출력하는 함수 / 매수 주문 시 단가로 활용/ 1차 호가주문으로 활용해보자
    instStockMst.SetInputValue(0,will_buy_item)
    instStockMst.BlockRequest()

    item_buy_hoga_1 = instStockMst.GetDataValue(1,0)  # 매수 1차 호가 // 매수 주문 시 활용
    item_buy_hoga_2 = instStockMst.GetDataValue(1, 1)
    item_buy_hoga_3 = instStockMst.GetDataValue(1, 2)
    item_sell_hoga_1 = instStockMst.GetDataValue(0, 0)  # 매도 1차 호가
    item_sell_hoga_2 = instStockMst.GetDataValue(0, 1)
    item_sell_hoga_3 = instStockMst.GetDataValue(0, 2)

    date = datetime.now().strftime('%D')
    timenow = datetime.now().strftime('%H:%M')
    print('[',date,timenow,']','호가정보입니다요.')
    print(instStockMst.GetDataValue(0,2))
    print(instStockMst.GetDataValue(0,1))
    print(instStockMst.GetDataValue(0,0))
    print('--------------------')
    print(instStockMst.GetDataValue(1,0))
    print(instStockMst.GetDataValue(1,1))
    print(instStockMst.GetDataValue(1,2))

    return (item_buy_hoga_1,item_buy_hoga_2,item_buy_hoga_3,
            item_sell_hoga_1,item_sell_hoga_2,item_sell_hoga_3)

#매수 정보 반환 함수
def buy_possible(will_buy_item,buy_hoga):  # 매수를 위한 정보 / 호가 정보를 인수롤 받아오도록 수정해야함.
    instCpTdNew5331A.SetInputValue(0, accountNumber) # 계좌번호
    instCpTdNew5331A.SetInputValue(1, accFlag[0]) # 상품관리 구분 코드
    instCpTdNew5331A.SetInputValue(2, will_buy_item) # 2 - (string) 종목코드[default:""]- 수량조회시입력
    instCpTdNew5331A.SetInputValue(3, '01') #일반/ fok로 주문하면될듯
    instCpTdNew5331A.SetInputValue(4, buy_hoga) # 4 - (long) 주문단가[default:0] - 수량조회시입력
    instCpTdNew5331A.SetInputValue(5, 'Y') # 5 - Y:증거금 100 %
    instCpTdNew5331A.SetInputValue(6, ord('2')) # 6 - (char)조회구분코드; '1'=금액조회[default], '2'=수량조회
    instCpTdNew5331A.BlockRequest()

    possible_amount = int(instCpTdNew5331A.GetHeaderValue(10)) # 증거금 100% 가능 금액 조회
    possible_quant = int(instCpTdNew5331A.GetHeaderValue(18)) # 증거금 100% 주문 가능 수량 조회

    print('주문가능금액:',possible_amount)
    print('주문가능수량:',possible_quant,'\n입니다요')
    return (possible_quant,possible_amount)

#매수 주문 함수
def buy_order(item,quant,hoga): # 매수주문
    instCpTd0311.SetInputValue(0,'2')
    instCpTd0311.SetInputValue(1,accountNumber)
    instCpTd0311.SetInputValue(2,accFlag[0])
    instCpTd0311.SetInputValue(3,item)
    instCpTd0311.SetInputValue(4,quant)
    instCpTd0311.SetInputValue(5,hoga)
    instCpTd0311.SetInputValue(7,'2') #FOK
    instCpTd0311.SetInputValue(8,'01') #01보통 03시장가 13최우선지정가
    instCpTd0311.BlockRequest()

#계좌 수익률 반환 함수
def benefit_ratio():  # 계좌 수익률을 출력하는 함수 / 매도 감시 시 활용

    instCpTd6033.SetInputValue(0,accountNumber)
    instCpTd6033.SetInputValue(1,accFlag[0])
    instCpTd6033.SetInputValue(3,'1')
    instCpTd6033.BlockRequest()

    #print(instCpTd6033.GetHeaderValue(8))  # 수익률 / 수익률을 기준으로 손절 익절 매도주문을 진행 / 수수료 감안해야함
    ratio = instCpTd6033.GetDataValue(11,0)
    return ratio

#호가 출력 및 반환 함수
def save_hoga_data(savestock_code):  # 호가 정보를 출력하는 함수 / 매도 주문 시 단가로 활용/ 1차 호가주문으로 활용해보자

    instStockMst.SetInputValue(0, savestock_code)
    instStockMst.BlockRequest()

    save_buy_hoga_1 = instStockMst.GetDataValue(1, 0)  # 매수 1차 호가 // 매수 주문 시 활용
    save_buy_hoga_2 = instStockMst.GetDataValue(1, 1)
    save_buy_hoga_3 = instStockMst.GetDataValue(1, 2)
    save_sell_hoga_1 = instStockMst.GetDataValue(0, 0)  # 매도 1차 호가
    save_sell_hoga_2 = instStockMst.GetDataValue(0, 1)
    save_sell_hoga_3 = instStockMst.GetDataValue(0, 2)

    dateprint = '['+ datetime.now().strftime('%D') +' '+ datetime.now().strftime('%H:%M') + ']'
    print(dateprint,'호가정보입니다요.')
    print(instStockMst.GetDataValue(0,2))
    print(instStockMst.GetDataValue(0,1))
    print(instStockMst.GetDataValue(0,0))
    print('--------------------')
    print(instStockMst.GetDataValue(1,0))
    print(instStockMst.GetDataValue(1,1))
    print(instStockMst.GetDataValue(1,2))

    return (save_buy_hoga_1,save_buy_hoga_2,save_buy_hoga_3,
            save_sell_hoga_1,save_sell_hoga_2,save_sell_hoga_3)

# 매도감시 함수 / 수익률이 익절선, 손절선 만족 시 매도 주문 실행 / 장중에만 실행시키려면?
def sell_obsever():
    print('매도 감시중입니다요. 주인님')
    savestock_name, savestock_quant, savestock_code = bought_item()
    check = 0
    #ratio_count = 0  # 임시로 무한루프를 종료하기 위한 기능
    while check == 0:
        time.sleep(1)
        now = int(datetime.now().strftime('%H%M'))
        ratio = benefit_ratio()

        dateprint = '['+ datetime.now().strftime('%D') +' '+ datetime.now().strftime('%H:%M') + ']'
        print(dateprint,savestock_name,'종목의 현재수익률입니다요:',ratio)

        if ratio > 101.5: # 익절
            print('얏호 익절 신호입니다요')
            check = 1
            return 1
        elif ratio < 95: # 손절
            print('손절입니다 도망치십시요~!')
            check = 1
            return 1
        if now > 1530:
            check = 1
            continue


#매도주문 함수
def sell_order(item,quant,hoga):  # 매도주문
    instCpTd0311.SetInputValue(0,'1') # 매도
    instCpTd0311.SetInputValue(1,accountNumber)
    instCpTd0311.SetInputValue(2,accFlag[0])
    instCpTd0311.SetInputValue(3,item)
    instCpTd0311.SetInputValue(4,quant)
    instCpTd0311.SetInputValue(5,hoga)
    instCpTd0311.SetInputValue(7,'0')  # 0.없음, 1.ioc, 2.fok
    instCpTd0311.SetInputValue(8,'01')
    instCpTd0311.BlockRequest()


#계좌별 잔고 평가 현황
def balance_check():
    instCpTd6033.SetInputValue(0,accountNumber)
    instCpTd6033.SetInputValue(1,accFlag[0])
    instCpTd6033.BlockRequest()

    balance = instCpTd6033.GetHeaderValue(3)
    return balance

#연결 여부 체크
connect_check()

#타겟 리스트 셋팅
#targetsavetxt()
target_list = target_list_read_txt()  # target_list 호출 //

#현재 시간 호출
now = int(datetime.now().strftime('%H%M'))

a = instCpConclusion.GetHeaderValue("1")
print(a)



# 시간이  9시00분 전이거나 15시30분 이후면 장외 대기
while now < 900:
    now = int(datetime.now().strftime('%H%M'))
    print('장 전 입니다요.')
    time.sleep(20)

# 시간이 9시 이상이거나 15시 30분보다 작으면 장 중으로 코드 수행
print('장이 열립니다요!')
while now >= 900 and now < 1530:  #장 중에만 반복   # 테스트시 1
    now = int(datetime.now().strftime('%H%M'))
    # 보유종목 체크
    boughtcheck = bought_check()  # 0:미보유중 1:보유중
    #보유 종목이 있을 경우 매도감시 및 매도주문
    if boughtcheck == 1:
        print('보유종목 정보를 가져와보겠습니다요')
        savestock_name,savestock_quant,savestock_code = bought_item()
        dateprint = '['+ datetime.now().strftime('%D') +' '+ datetime.now().strftime('%H:%M') + ']'
        rate = benefit_ratio()
        printsave(dateprint,savestock_name,'종목을',savestock_quant,'주 보유중입니다요 수익률:',rate)

        #sell_check로 익절 및 손절 반복 감시 수행
        sell_check = sell_obsever()
        if sell_check == 1 : #매도 신호 확인 시 매도 정보 추출
            print('매도 신호입니다요!!') # 매수 1호가에 익절
            save_buy_hoga_1, save_buy_hoga_2, save_buy_hoga_3,\
            save_sell_hoga_1, save_sell_hoga_2, save_sell_hoga_3\
            = save_hoga_data(savestock_code)
            dateprint = '['+ datetime.now().strftime('%D') +' '+ datetime.now().strftime('%H:%M') + ']'
            rate = benefit_ratio()
            printsave(dateprint,savestock_name,'종목',savestock_quant,'주를   ',save_buy_hoga_1,\
                  '원에 매도 주문 신청합니다요 수익률:',rate)
            instCpTdUtil.TradeInit()
            sell_order(savestock_code,savestock_quant,save_buy_hoga_1)
            printsave('매도 주문 완료입니다 주인님')
            print('매도 체결 대기 중입니다요.')
            # 재진입 지양
            target_list.remove(savestock_code)
            # savestock_name이 none이 되면 보유 종목이 없는 것.

            print("매도 결과 확인중입니다요.")

            savestock_quant_2 = savestock_quant
            now_before = int(datetime.now().strftime('%H%M'))
            while savestock_quant == savestock_quant_2:  # 주문수량과 매도후 잔량이 같으면
                now = int(datetime.now().strftime('%H%M'))
                time.sleep(1)
                avestock_name, savestock_quant_2, savestock_code = bought_item() # 매도 후 잔량 리셋
                if savestock_quant_2 == 0: # 매도 완료
                    dateprint = '[' + datetime.now().strftime('%D') + ' ' + datetime.now().strftime('%H:%M') + ']'
                    printsave(dateprint, '매도 완료입니다요')
                    break
                if savestock_quant != savestock_quant_2: # 일부 매도
                    dateprint = '[' + datetime.now().strftime('%D') + ' ' + datetime.now().strftime('%H:%M') + ']'
                    printsave(dateprint, '일부 매도 완료입니다요')
                    break

                if now-now_before > 10 : # 10분이 초과하면 break
                    dateprint = '[' + datetime.now().strftime('%D') + ' ' + datetime.now().strftime('%H:%M') + ']'
                    printsave(dateprint, '매도 실패하였습니다요.')
                    break

                if now > 1531:
                    print("장이 마감하였습니다요")


            print('매도, 매수 감시로 돌아갑니다요')
            boughtcheck = bought_check()
            continue


    # 보유종목이 없을 경우 매수 종목 탐색
    if boughtcheck == 0 :
        #계좌체크
        possible_amount = balance_check()
        print("주인님, 총알입니다요 : ",possible_amount)
        
        will_buy_item = buy_observer(instStockChart,target_list)
        will_buy_item_name = instCpStockCode.CodeToName(will_buy_item[0])
        item_buy_hoga_1, item_buy_hoga_2, item_buy_hoga_3,\
        item_sell_hoga_1, item_sell_hoga_2, item_sell_hoga_3\
        =item_hoga_data(will_buy_item[0])

        if item_sell_hoga_1 == 0:
            print("상한가종목입니다요")
            item_sell_hoga_1 = item_buy_hoga_1


        possible_quant = int(possible_amount / item_sell_hoga_1)

        if possible_quant == 0:
            print('총알이 부족합니다요,')
            print('다른 종목을 찾습니다요')
            target_list.remove(will_buy_item[0])
            if len(target_list) == 0:
                print('살 수 있는 종목이 없습니다요')
                quit()
            continue

        if possible_quant > 0:
            print('매수를 진행합니다요')
            dateprint = '['+ datetime.now().strftime('%D') +' '+ datetime.now().strftime('%H:%M') + ']'
            printsave(dateprint,will_buy_item_name,'종목',possible_quant,'주를',
                  item_sell_hoga_1,'원에 매수합니다요')
            
            instCpTdUtil.TradeInit()   # 주문 초기화
            buy_order(will_buy_item[0],possible_quant,item_sell_hoga_1)    # 매수1호가 주문 /
            print('매수주문을 완료하였습니다요')

            print('체결 완료 대기중입니다요')
            buy_complete_check = 0
            time_check_a = int(datetime.now().strftime('%H%M'))
            while buy_complete_check == 0 :
                savestock_name, savestock_quant, savestock_code\
                =bought_item()
                time.sleep(1)
                # 매수 주문 완료 후 시간 체크
                time_check_b =int(datetime.now().strftime('%H%M'))
                if time_check_b - time_check_a > 5:      # 매수타이머 5분/
                    printsave('5분 초과하여 재탐색합니다요')
                    print('종목 재검색을 합니다요.')
                    target_list.remove(will_buy_item[0])
                    buy_complete_check = 1
                    continue

                if possible_quant == savestock_quant:
                    buy_complete_check = 1
                    date = datetime.now().strftime('%D')
                    timenow = datetime.now().strftime('%H:%M')
                    printsave(']',date,timenow,']','매수 체결 완료입니다요.')
                    continue



# 15시 30분 이후 타겟종목 저장 작업 수행
now = int(datetime.now().strftime('%H%M'))
if now > 1530:
    print('targetlist를 추출합니다.')
    targetsavetxt()
    print('종목추출완료, 프로그램 종료합니다요.')
    quit()


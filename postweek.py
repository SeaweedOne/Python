#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def getYearweek(yearweek, option):

    if type(option) == str : option = int(option)       #option이 str로 입력됐을 때 int로 변환

    if type(yearweek) == int : yearweek = str(yearweek) #yearweek이 int로 입력됐을 때 str로 변환

    inputYear = int(yearweek[:4])

    inputWeek = int(yearweek[4:])

    newWeek = inputWeek

    i = 1

 

    if (inputWeek <= option)  :  

        while ((newWeek <= option)==True):  #누적받는 newweek 이 option보다 작은동안 while문을 돌린다.

            newYear = inputYear - i         #입력년도 - i를 이용해 년도 수를 줄여나간다.

            newWeek = newWeek + Week.last_week_of_year(newYear).week #해당 년도의 maxweek값을 구해 newweek에 더해준다.

            i = i +1

 

            if (newWeek > option) :      #만약 newweek이 option보다 커지면 newweek-option 실행 후 break

                result = str(newWeek - option) 

                if len(result) == 1 :  

                    result = "0" + result 

                break

        return str(newYear) + str(result) #줄어든 year과 결과값을 문자열로 변경해 이어준다.

 

    else : #week이 option보다 큰 경우 

        result =  str(inputWeek - option)

        if len(result) == 1 :

            result = "0" + result

            result = str(inputYear) + result

            return result

        else: 

            result = str(inputYear) + result

            return result


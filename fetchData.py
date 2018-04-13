#!/usr/bin/env python
# -*- coding: utf-8 -*-

#https://ethplorer.io/address/

import csv
import codecs
import urllib.request
import datetime
import hashlib
import json
from pprint import pprint


now = datetime.datetime.now()

#ethAddress = "0xebd9366375692ac6dd97e56cf1c801d7bcb1de69"#
#ethAddress = "0xd0a6e6c54dbc68db5db3a091b171a77407ff7ccf"
ethAddress = "0x487b4D55459DE9c5A15e7f3f59654F8E1d58e868"
ethAddress = ethAddress.lower()

#addresses to search
addressEOS = "0x86Fa049857E0209aa7D9e616F7eb3b3B78ECfdb0"
snapshotDate = datetime.datetime.strptime("2018-02-28 00:01:00", "%Y-%m-%d %H:%M:%S" )
EOS_LIMIT_AMOUNT = 1
ETHEREUM_LIMIT_AMOUT = 0.1

class CryptoAmount:
    def parseLine(self, line, currentAddress, tokenAddress):
        if line[5].upper() != tokenAddress.upper():
            return 0

        print (currentAddress)
        print (line[2])
        print (line[3])
        isCurrentAddressReceiver = True if line[3] == currentAddress else ( False if line[2] == currentAddress else "unvalid address")
        if isCurrentAddressReceiver == "unvalid address":
            return 0

        value = 0.0
        try:
            value = float(line[5])
        except ValueError as ex:
            return 0
        return value if isCurrentAddressReceiver else value * -1



    def parseAllLines(self, data, currentAddress):
        EOSIncomeSum = 0
        EOSOutcomeSum = 0
        ETHIncomeSum = 0
        ETHOutcomeSum = 0

        for line in data:
            print (line)
            if len(line) != 8:
                continue
            if line[0] == 'date':
                continue

            #checking the date
            parsedTime = datetime.datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S")
            if parsedTime >= snapshotDate:
                continue

            print(line[5])
            #is EOS line
            if line[5].upper() == addressEOS.upper():
                EOSvalue = self.parseLine(line, currentAddress, addressEOS)
                EOSIncomeSum += EOSvalue if EOSvalue > 0 else 0
                EOSOutcomeSum += EOSvalue if EOSvalue < 0 else 0

        #check EOS ballance
        if EOSIncomeSum - EOSOutcomeSum > EOS_LIMIT_AMOUNT:
            return True
        return False

    def checkBallanceEOS(self, currentAddress):
        now = datetime.datetime.now()
        currentDate = now.strftime("%Y-%m-%d").replace("-0", "-")

        m = hashlib.md5()
        URL_ADDRESS = "https://ethplorer.io/service/csv.php?data=" + currentAddress
        PATH = "/service/csv.php?data=" + currentAddress

        m.update((PATH + currentDate).encode('utf-8'))
        urlTORetreiveData = URL_ADDRESS + "&hash=" + m.hexdigest()
        retreivedData = ""
        response = urllib.request.urlopen(urlTORetreiveData)
        print (urlTORetreiveData)

        retreivedData = csv.reader(codecs.iterdecode(response, 'utf-8'), delimiter=';')
        self.parseAllLines(retreivedData, currentAddress)
        return True
        #print (type(retreivedData))
        #for line in retreivedData:
        #    #print(line)
        #    parsedLine = line[0].split(";")
        #    print (parsedLine)

        #print(retreivedData)

    def checkEOSBallance(self, currentAddress):
        try:
            limitTimestamp = 1519862405
            PATH_EOS_INCOME = "https://api.ethplorer.io/getAddressHistory/" + currentAddress + "?apiKey=freekey&token=0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0&type=transfer&limit=100"
            response = urllib.request.urlopen(PATH_EOS_INCOME)
            string = response.read().decode('utf-8')
            dataStructure = json.loads(string)

            EOSIncomeSum = 0
            EOSOutcomeSum = 0
            isMoreThanLimitBeforeDate = False

            for item in dataStructure["operations"]:
                if 'value' not in item: continue
                if 'type' not in item: continue
                if 'from' not in item: continue
                if 'to' not in item: continue
                if 'timestamp' not in item: continue

                value = 0
                timestamp = 0
                try:
                    value = int(item["value"])/1000000000000000000
                    timestamp = int(item["timestamp"])
                except ValueError as ex:
                    continue

                #after limit
                if timestamp > limitTimestamp:
                    continue

                isCurrentAddressReceiver = True if item["to"].lower() == currentAddress.lower() else ( False if item["from"].lower() == currentAddress.lower() else "unvalid address")
                if isCurrentAddressReceiver == "unvalid address": continue

                if value > EOS_LIMIT_AMOUNT:
                    isMoreThanLimitBeforeDate = True

                EOSIncomeSum += value if isCurrentAddressReceiver == True else 0
                EOSOutcomeSum += value if isCurrentAddressReceiver == False else 0

            if (EOSIncomeSum - EOSOutcomeSum) >= EOS_LIMIT_AMOUNT:
                return 1
            if isMoreThanLimitBeforeDate:
                return 2
            return 0
        except Exception as e:
            return 0

    def getETHBallance(self, currentAddress):
        try:
            API_TOKEN = "XXXXX"
            BLOCK_LOWER_LIMIT = 4865131
            BLOCK_LIMIT = 5065207
            URL_ADDRESS = "https://api.etherscan.io/api?module=account&action=txlist&address="

            url = URL_ADDRESS + currentAddress + "&startblock=" + str(BLOCK_LOWER_LIMIT) + "&endblock=" + str(BLOCK_LIMIT) + "&sort=desc&apikey=" + API_TOKEN
            response = urllib.request.urlopen(url)

            string = response.read().decode('utf-8')
            dataStructure = json.loads(string)
            print (len(dataStructure['result']))
            for item in dataStructure['result']:
                print (item)
        except Exception as e:
            return 0
    def getETHBalanceOnBlock(self, currentAddress):
        try:
            URL_ADDRESS = "https://api.blockcypher.com/v1/eth/main/addrs/"
            BLOCK_LIMIT = 5174125
            url = URL_ADDRESS + currentAddress + "/balance?after=" + str(BLOCK_LIMIT-1) +"&before=" + str(BLOCK_LIMIT) +"?token=TOKEN"
            response = urllib.request.urlopen(url)
            string = response.read().decode('utf-8')
            dataStructure = json.loads(string)
            balance = dataStructure['balance']/1000000000000000000
            return 1 if balance >= ETHEREUM_LIMIT_AMOUT else 0
        except: #urllib.error.HTTPError:
            return -1



if __name__ == '__main__':
    a = CryptoAmount().getETHBalanceOnBlock("0xf2b409Fd15B0535DF20B9E1AD580b7c5B28979c0")
    print (a)














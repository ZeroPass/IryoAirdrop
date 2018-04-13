# pip install azure-storage
import azure
from azure.storage.table import TableService, Entity
from azure.storage.file import FileService, ContentSettings
from datetime import datetime, timedelta, time

import traceback
import logging

TIME_DURATION_LIMIT = 15

table_service = TableService(account_name='accountNameXXXXX', account_key='Big secret:)')

def createDatabases():
    try:
        if table_service.exists('participants') == False:
            table_service.create_table('participants')
        if table_service.exists('participantReferrer') == False:
            table_service.create_table('participantReferrer')
    except Exception as e:
        logging.error(traceback.format_exc())

def addNewParticipant(id, address, ownReferralLink, isConfirmed, isCompleted = False, invitedReferral = ''):
    try:
        task = Entity()
        task.PartitionKey = 'participant'
        task.RowKey = "participant_" + str(id)
        task.userID = id
        task.ethereumAddress = address
        task.referral = ownReferralLink
        task.invitedReferralLink = invitedReferral
        task.isConfirmed = isConfirmed
        task.isCompleted = isCompleted
        task.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task.version = 1
        table_service.insert_or_replace_entity('participants', task)
    except Exception as e:
        logging.error(traceback.format_exc())

def updateParticipantComplete(id, referrerCode = ''):
    try:

        if referrerCode != '':
            addReferralToMainUser(id, referrerCode)
        else:
            item = table_service.get_entity('participants', 'participant', "participant_" + str(id))
            item.isCompleted = True
            item.isConfirmed = True
            table_service.insert_or_replace_entity('participants', item)
    except Exception as e:
        logging.error(traceback.format_exc())

def addReferralToMainUser(id, referralLink):
    try:
        task = Entity()
        task.PartitionKey = 'referral_' + referralLink
        task.RowKey = "referral_" + str(id)
        task.userID = id
        task.referral = referralLink
        task.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task.version = 1
        table_service.insert_or_replace_entity('participantReferrer', task)

        #update participant
        item = table_service.get_entity('participants', 'participant', "participant_" + str(id))
        item.isConfirmed = True
        item.isCompleted = True
        item.invitedReferralLink = referralLink
        table_service.insert_or_replace_entity('participants', item)

    except Exception as e:
        logging.error(traceback.format_exc())

def addEOSToMainUser(id, eosAddress):
    try:
        #update participant
        item = table_service.get_entity('participants', 'participant', "participant_" + str(id))
        item.eosAddress = eosAddress
        table_service.insert_or_replace_entity('participants', item)

    except Exception as e:
        logging.error(traceback.format_exc())

def isReferralTimeCorrect(id):
    try:
        now = datetime.now()
        item = table_service.get_entity('participants', 'participant', "participant_" + str(id))
        itemDate = datetime.strptime(item.datetime, "%Y-%m-%d %H:%M:%S")
        itemDatePlusLimit = itemDate + timedelta(minutes = TIME_DURATION_LIMIT)
        return True if now < itemDatePlusLimit else False
    except Exception as e:
        logging.error(traceback.format_exc())


def importALotOfRows():
    for a in range(1,1100):
        task = Entity()
        task.PartitionKey = 'participant'
        task.RowKey = "participant_" + str(a)
        task.userID = a
        task.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task.version = a
        table_service.insert_or_replace_entity('participants', task)

def getall():
    i = 0
    next_pk = None
    next_rk = None
    part_k = "PartitionKey eq 'participant'"
    counter = 0
    while True:
        entities = table_service.query_entities('participants', filter=part_k, next_partition_key=next_pk, next_row_key=next_rk, top=1000)
        i += 1
        for ent in entities:
            counter = counter + 1
        if hasattr(entities, 'x_ms_continuation'):
            x_ms_continuation = getattr(entities, 'x_ms_continuation')
            next_pk = x_ms_continuation['nextpartitionkey']
            next_rk = x_ms_continuation['nextrowkey']
        else:
            break;
    return counter

def GetData():
    keyMarkers = {}
    keyMarkers['nextpartitionkey'] = 0
    keyMarkers['nextrowkey'] = 0
    #b=[]
    counter = 0
    while True:
        #get a batch of data
        a = table_service.query_entities(table_name="participants", filter="PartitionKey eq 'participant'" ,num_results=1000 ,marker=keyMarkers)
        #copy results to list
        for item in a.items:
            counter = counter + 1
        #check to see if more data is available
        if len(a.next_marker) == 0:
            del a
            break
        #if more data available setup current position
        keyMarkers['nextpartitionkey'] = a.next_marker['nextpartitionkey']
        keyMarkers['nextrowkey'] = a.next_marker['nextrowkey']
        #house keep temp storage
        del a
    #return final list
    return counter

def isReferralExists(referral):
    try:
        #entities = table_service.query_entities('participants', filter="PartitionKey eq 'participant'")
        #for entity in entities:
        #    if entity.referral == referral:
        #        return True
        #return False

        keyMarkers = {}
        keyMarkers['nextpartitionkey'] = 0
        keyMarkers['nextrowkey'] = 0
        while True:
            # get a batch of data
            a = table_service.query_entities(table_name="participants", filter="PartitionKey eq 'participant'",
                                             num_results=1000, marker=keyMarkers)
            # copy results to list
            for item in a.items:
                try:
                    if item.referral == referral:
                        return True
                except Exception as e:
                    print("No referral found")
            # check to see if more data is available
            if len(a.next_marker) == 0:
                del a
                break
            # if more data available setup current position
            keyMarkers['nextpartitionkey'] = a.next_marker['nextpartitionkey']
            keyMarkers['nextrowkey'] = a.next_marker['nextrowkey']
            # house keep temp storage
            del a
        return False
    except Exception as e:
        print (traceback.format_exc())
        return False


def stat():
    try:
        keyMarkers = {}
        keyMarkers['nextpartitionkey'] = 0
        keyMarkers['nextrowkey'] = 0
        statDict= {}
        while True:
            # get a batch of data
            a = table_service.query_entities(table_name="participants", filter="PartitionKey eq 'participant'",
                                             num_results=1000, marker=keyMarkers)
            # copy results to list
            for item in a.items:
                itemDate = datetime.strptime(item.datetime, "%Y-%m-%d %H:%M:%S")
                printDate = itemDate.strftime('%d/%m/%Y')
                cameWithReferral = 0
                try:
                    if hasattr(item, 'invitedReferralLink') and item.invitedReferralLink != '':
                        cameWithReferral = 1
                except azure.common.AttributeError:
                    cameWithReferral = 0

                if printDate not in statDict:
                    statDict[printDate] = (1, cameWithReferral)
                else:
                    statDict[printDate] = (statDict[printDate][0] + 1, statDict[printDate][1] + cameWithReferral)

            # check to see if more data is available
            if len(a.next_marker) == 0:
                del a
                break
            # if more data available setup current position
            keyMarkers['nextpartitionkey'] = a.next_marker['nextpartitionkey']
            keyMarkers['nextrowkey'] = a.next_marker['nextrowkey']
            # house keep temp storage
            del a
        return statDict
    except Exception as e:
        logging.error(traceback.format_exc())

def isUserExists(id):
    try:
        try:
            item = table_service.get_entity('participants', 'participant', "participant_" + str(id))
            return True
        except azure.common.AzureMissingResourceHttpError:
            return False
    except Exception as e:
        logging.error(traceback.format_exc())

def isEOSAddressExists(id):
    try:
        try:
            item = table_service.get_entity('participants', 'participant', "participant_" + str(id))
            return item.eosAddress
        except azure.common.AzureMissingResourceHttpError:
            return ""
    except Exception as e:
        return ""

def getReferralLink(id):
    try:
        try:
            item = table_service.get_entity('participants', 'participant', "participant_" + str(id))
            return item.referral
        except azure.common.AzureMissingResourceHttpError:
            return ""
    except Exception as e:
        logging.error(traceback.format_exc())

def getMyReferral(id):
    try:
        try:
            item = table_service.get_entity('participants', 'participant', "participant_" + str(id))
            return item.invitedReferralLink
        except azure.common.AzureMissingResourceHttpError:
            return ""
    except Exception as e:
        logging.error(traceback.format_exc())

def getReferralCount(id):
    try:
        try:
            referralLink = getReferralLink(id)
            if referralLink == "":
                return 0
            entities = table_service.query_entities('participantReferrer', filter="PartitionKey eq 'referral_"+ referralLink + "'")
            return len(entities.items)
        except azure.common.AzureMissingResourceHttpError:
            return ""
    except Exception as e:
        logging.error(traceback.format_exc())

def getParticipantsCount():
    try:
        totalSize = 0
        keyMarkers = {}
        keyMarkers['nextpartitionkey'] = 0
        keyMarkers['nextrowkey'] = 0
        while True:
            # get a batch of data
            a = table_service.query_entities(table_name="participants", filter="PartitionKey eq 'participant'",
                                             num_results=1000, marker=keyMarkers)
            totalSize += len(a.items)
            # check to see if more data is available
            if len(a.next_marker) == 0:
                del a
                break
            # if more data available setup current position
            keyMarkers['nextpartitionkey'] = a.next_marker['nextpartitionkey']
            keyMarkers['nextrowkey'] = a.next_marker['nextrowkey']
            # house keep temp storage
            del a
        return totalSize
    except Exception as e:
        return 0

def getParticipantsCountOverLimit():
    try:
        LIMIT = 22500
        totalSize = 0
        keyMarkers = {}
        keyMarkers['nextpartitionkey'] = 0
        keyMarkers['nextrowkey'] = 0
        while True:
            # get a batch of data
            a = table_service.query_entities(table_name="participants", filter="PartitionKey eq 'participant'",
                                             num_results=1000, marker=keyMarkers)
            totalSize += len(a.items)
            # check to see if more data is available
            if len(a.next_marker) == 0:
                del a
                break
            # if more data available setup current position
            keyMarkers['nextpartitionkey'] = a.next_marker['nextpartitionkey']
            keyMarkers['nextrowkey'] = a.next_marker['nextrowkey']
            # house keep temp storage
            del a
        return True if totalSize > LIMIT else False
    except Exception as e:
        return 0

def getParticipantsCountTodayOverLimit():
    try:
        LIMIT = 2000
        totalSize = 0
        today = datetime.now().strftime("%Y-%m-%d")
        curentTime = datetime.now().time()
        restartTime = time(12)
        if curentTime < restartTime:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            filter = "PartitionKey eq 'participant' and Timestamp ge datetime'" + yesterday + "T12:00:00' and Timestamp le datetime'" + today + "T11:59:00'"
        else:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            filter= "PartitionKey eq 'participant' and Timestamp ge datetime'" + today + "T12:00:00' and Timestamp le datetime'" + tomorrow + "T11:59:00'"
        keyMarkers = {}
        keyMarkers['nextpartitionkey'] = 0
        keyMarkers['nextrowkey'] = 0
        while True:
            # get a batch of data
            a = table_service.query_entities(table_name="participants",
                                             filter=filter,
                                             num_results=1000, marker=keyMarkers)
            totalSize += len(a.items)
            # check to see if more data is available
            if len(a.next_marker) == 0:
                del a
                break
            # if more data available setup current position
            keyMarkers['nextpartitionkey'] = a.next_marker['nextpartitionkey']
            keyMarkers['nextrowkey'] = a.next_marker['nextrowkey']
            # house keep temp storage
            del a
        return True if totalSize > LIMIT else False
    except Exception as e:
        return 0
    """
    try:
        LIMIT = 999
        today = datetime.now().strftime("%Y-%m-%d")
        keyMarkers = {}
        # get a batch of data
        a = table_service.query_entities(table_name="participants", filter="PartitionKey eq 'participant' and Timestamp ge datetime'" + today + "T00:00:00' and Timestamp le datetime'" + today + "T23:59:00'",
                                         num_results=1000, marker=keyMarkers)

        return True if len(a.items) > LIMIT else False

    except Exception as e:
        return 0"""


if __name__ == '__main__':
    a = getParticipantsCountTodayOverLimit()
    print (a)
    #importALotOfRows()
    #print(str(GetData()))
    #statistic = stat()
    #print ("Date        |   New users (with referrals)")
    #for item in statistic:
    #    print(str(item) + "  |   " + str(statistic[item][0]) + " (" + str(statistic[item][1]) + ")")
    #createDatabases()
    #addNewParticipant(1234, '0xgjsdghsdfgsdf', "5hu8d", "7fkdjd")
    #addReferralToMainUser(3453, "7fkdjd")
    #print ("bula: " + str(getReferralCount(1234)))

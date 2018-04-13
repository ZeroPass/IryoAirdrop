#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pa ax | grep airdropBot

import sys

sys.path.append("/home/adminiryo/IryoAirdrop/AirdropBot")
sys.path.append("/home/adminiryo/IryoAirdrop/AirdropBot/IryoAirdrop")
sys.path.append("/home/adminiryo/IryoAirdrop/AirdropBot/IryoAirdrop/groupUsers")
sys.path.append("/home/adminiryo/IryoAirdrop/AirdropBot/IryoAirdrop/EOS")

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
import re

#from IryoAirdrop.groupUsers.fetcher import TelegramGroupChecker
#from IryoAirdrop.hashids import Hashids
#from IryoAirdrop.fetchData import CryptoAmount
#import IryoAirdrop.EOS.eosAddress as EOSchecker
#import IryoAirdrop.storage as Storage

from hashids import Hashids
from fetchData import CryptoAmount
import storage as Storage
import eosAddress as EOSchecker
from fetcher import TelegramGroupChecker

BOT_TOKEN = "XXX:XXXXX"
#BOT_TOKEN = "XXX:XXXX"
SALT = "verySaltyXXXX"
IRYO_GROUP = "someGroup"
IRYO_CHANNEL = "someChannel"
BONUS = 20

ARTICLE = "https://telegra.ph/Iryo-Airdrop-Walkthrough-03-14"

SECRET = 'really big secret:)'

PARTICIPATE = 'Participate'
REGISTER_EOS_ADDRESS = 'Update EOS address'
INFO = 'Info'
REFERRAL_CODE = 'Referral code'
YOUR_BONUS = 'Your bonus'
HELP = 'Help'

checkGroup = TelegramGroupChecker()
checkGroup.connect()


bot_keyboard = [[PARTICIPATE, REGISTER_EOS_ADDRESS, INFO, HELP]]


def calculateRefferalCode(hash):
    if hash == '':
        return ''
    hashids = Hashids(salt=SALT, min_length=7, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789')
    hashid = hashids.encode(hash)
    return hashid


def checkReferralCode(refferalCode):
    return True if re.search(r"^[A-Z1-9]{7,}$", refferalCode) else False


def checkEthereumAddressStructure(address):
    return True if re.search(r"^0x[a-fA-F0-9]{40}$", address) else False

def checkEOSaddressStructure(address):
    if re.search(r'^EOS[a-zA-Z0-9]{50}$', address) == False:
        return False
    if EOSchecker.verify_address(address) == False:
        return False
    return True

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

NO_STATE, ENTER_REFERRAL, ENTER_EOS_ADDRESS, CHECK_EOS_ADDRESS = range(4)


def start(bot, update):
    ##
    img = open('start.webp', 'rb')
    bot.send_sticker(chat_id=update.message.chat_id,
                     sticker=img,
                     reply_markup=ReplyKeyboardRemove())

    update.message.reply_text(
        "Hi! I am Iryo Airdrop Bot, deployed by the Iryo team.\n"
        "My job is to get you some free Iryo tokens!\n"
        "I don’t want to bore you with the details, so go ahead and check out this walkthrough guide " + ARTICLE + " before interacting with me!\n"
                                                                                                                   "To participate you’ll need to do 2 things:\n\n"

                                                                                                                   "🎯 Join the Iryo telegram group & the alerts channel.\n"
                                                                                                                   "		• https://t.me/IRYOnetwork - Iryo’s primary group - join the conversation!\n"
                                                                                                                   "		• https://t.me/iryo_alerts - An important channel managed by the Iryo team (security alerts, contract address, etc)\n\n"

                                                                                                                   "🎯Tell us your valid Ethereum address on which at least one of next two conditions are true on March 1st, 2018. Block 5174125 https://etherscan.io/block/5174125\n"
                                                                                                                   "		• At least 0.1 ETH on your address.\n"
                                                                                                                   "		• At least 1 EOS token on your address.\n\n"

                                                                                                                   "Please enter your Ethereum address (Warning: An address from an exchange will not work, i.e Binance, Kraken etc.)",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE


def ethereumAddressReceived(bot, update, user_data):
    receivedText = update.message.text
    address = receivedText.strip()

    if Storage.getParticipantsCountOverLimit() == True:
        update.message.reply_text(
            "The Iryo Airdrop is complete! We distributed tokens to 22,500 participants!",
            reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE

    if Storage.getParticipantsCountTodayOverLimit() == True:
        update.message.reply_text(
            "Wow, slow down! We reached the 2,000 Airdrops per day limit. Come back tomorrow/today! (Timer resets at 12:00 gmt)",
            reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE

    update.message.reply_text("Checking structure of Ethereum address ...",
                              reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
    if (checkEthereumAddressStructure(address) == False):
        update.message.reply_text("Received address is not correct.\n" \
                                  "Please send me a correct address.",
                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE

    update.message.reply_text("Checking previous participants IDs and addresses ...",
                              reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
    if Storage.isUserExists(update.message.from_user.id):
        hashedID = calculateRefferalCode(update.message.from_user.id)
        update.message.reply_text("Your address or telegram ID already exists in database",
                                  #"     🎯Your referral code: " + hashedID + "\n\n"
                                  #"You can get additional Iryo tokens by sharing your referral code. Every user who successfully joins the airdrop will bring you 20% worth of additional bonus tokens. The number of people using your referral code is only limited by the campaign itself.",
                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE

    update.message.reply_text("Checking participation in Iryo group/channel ...",
                              reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))

    #isUserInGroup = checkGroup.isUserJoined(update.message.from_user.id, IRYO_GROUP)
    #IsUserInChannel = checkGroup.isUserJoined(update.message.from_user.id, IRYO_CHANNEL)
    #if (isUserInGroup == False or IsUserInChannel == False):
    #        text = ""
    #    if isUserInGroup == False and IsUserInChannel == True:
    #            text += "I can't seem to find you in the Iryo telegram group.\n" \
    #                "Join to our group ( https://t.me/IRYOnetwork ) and please send me your Ethereum address again."
    #    elif isUserInGroup == True and IsUserInChannel == False:
    #        text += "I can't seem to find you in the Iryo alerts channel.\n" \
    #                "Join to our channel ( https://t.me/iryo_alerts ) and please send me your Ethereum address again."
    #    else:
    #        text += "I can't seem to find you in either the Iryo group or in the alerts channel.\n\n" \
    #                "Please join the channel and the group below to get your Iryo tokens!\n" \
    #                "      • https://t.me/IRYOnetwork - main Iryo conversation group \n" \
    #                "      • https://t.me/iryo_alerts - important channel managed by Iryo team (security alerts, contract address, etc)\n\n" \
    #                "After joining, please send me your Ethereum address again."
    #    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True),
    #                              disable_web_page_preview=True)
    #    return NO_STATE

    hashedID = calculateRefferalCode(update.message.from_user.id)

    update.message.reply_text("Checking your balance on Ethereum address ...",
                              reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
    eosValueCode = CryptoAmount().checkEOSBallance(address)
    ethCode = CryptoAmount().getETHBalanceOnBlock(address)

    if ethCode == 0 and eosValueCode == 0:
        #Storage.addNewParticipant(update.message.from_user.id,
        #                          address,
        #                          hashedID,
        #                          True,
        #                          True)
        update.message.reply_text("Your address didn’t have enough EOS orETH on SNAPSHOT date."
                                    #"     🎯Your referral code: " + hashedID + "\n\n"
                                    #"Don't despair! You can still get Iryo tokens by sharing your referral code.\n "
                                    #"Every user who successfully joins the airdrop will bring you " + str(
                                    #BONUS) + "% of tokens(amount of tokens if you would get full airdrop portfolio). \n"
                                    #"The number of people who can use your referral code has no limit.\n"
                                    #"Every user that joins successfully brings you " + str(BONUS) + "% more tokens."
                                  ,
                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE
    elif ethCode == 0 and eosValueCode == 2:
        #Storage.addNewParticipant(update.message.from_user.id,
        #                          address,
        #                          hashedID,
        #                          True,
        #                          True)
        update.message.reply_text(
            "Your address didn’t have enough ETH  and you have a confusing EOS transaction history. Please contact support.",
            #"     🎯Your referral code: " + hashedID + "\n\n"
            #                                           "Every user who successfully joins the airdrop will bring you " + str(
            #    BONUS) + "% of tokens(amount of tokens if you would get full airdrop portfolio). \n"
            #             "The number of people who can use your referral code has no limit.\n"
            #             "Every successfully user that joins brings you " + str(BONUS) + "% more tokens.",
            reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE

    elif ethCode == -1:
        update.message.reply_text(
            "Bot has reached the limit of requests. Please try again later.",
            reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE

    Storage.addNewParticipant(update.message.from_user.id,
                              address,
                              hashedID,
                              True,
                              True)

    update.message.reply_text("Thank you for participating in the Iryo Airdrop campaign!\n"
                                "Your address is correct and the pre-conditions are met.\n\n"
                                  "🎯 New referrals have been suspended!\n"
                                "Read why here: https://medium.com/p/4dfd238bf225\n\n"
                                  "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
                                 "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
                              reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True),
                              disable_web_page_preview=True)

    #temp commented
    #update.message.reply_text("Thank you for participating in the Iryo Airdrop campaign!\n"
    #                            "Your address is correct and the pre-conditions are met.\n\n"
    #                              "Just one more thing. Please insert your EOS address (to get free Iryo token on EOS blockchain)\n"
    #                              "or\n"
    #                              "type /cancel to finish the process (and set EOS address later).\n",
    #                           reply_markup=ReplyKeyboardRemove(),
    #                            disable_web_page_preview=True)

    #temp commented
    #return ENTER_EOS_ADDRESS
    return NO_STATE


#not in use
#def donebutton(bot, update):
#    ##
#    img = open('100.webp', 'rb')
#    bot.send_sticker(chat_id=update.message.chat_id,
#                     sticker=img,
#                     reply_markup=ReplyKeyboardRemove())
#    hashedID = calculateRefferalCode(update.message.from_user.id)
#    Storage.updateParticipantComplete(update.message.from_user.id)
#    update.message.reply_text("Thank you for participating in the Iryo Airdrop campaign!\n\n"
#                              "     🎯Your referral code: " + hashedID + "\n\n"
#                              "You can get additional IRYO tokens by sharing your referral code. "
#                              "Every user who successfully joins the airdrop will bring you 20% additional bonus tokens. "
#                              "The number of people using your referral code is only limited by the campaign itself\n\n"
#                              "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
#                             "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
#                              reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
#    return NO_STATE


#def referralGot(bot, update):
#    receivedText = update.message.text
#    referralCode = receivedText.strip()
#    if Storage.isReferralTimeCorrect(update.message.from_user.id) == False:
#        hashedID = calculateRefferalCode(update.message.from_user.id)
#        Storage.updateParticipantComplete(update.message.from_user.id)
#
#        img = open('100.webp', 'rb')
#        bot.send_sticker(chat_id=update.message.chat_id,
#                         sticker=img,
#                         reply_markup=ReplyKeyboardRemove())
#
#        update.message.reply_text("Time to enter referral code of your friend is expired.\n\n"
#                                  "     🎯Your referral code: " + hashedID + "\n\n"
#                                                                             "You can get additional IRYO tokens by sharing your referral code. "
#                                                                             "Every user who successfully joins the airdrop will bring you 20% additional bonus tokens. "
#                                                                             "The number of people using your referral code is only limited by the campaign itself\n\n"
#                                                                             "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
#                                                                             "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
#                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
#
#        return NO_STATE
#
#    if checkReferralCode(referralCode) == False or Storage.isReferralExists(referralCode) == False:
#        update.message.reply_text("Referral code is not correct or not found in database.\n\n"
#                                  "   🎯Enter your friend's referral code now and you and your friend will receive 20% more tokens each! (Warning: You only have 15 minutes to do this!):\n\n"
#                                  "    or\n\n"
#                                  "   🎯Type or click /done to skip this step and finish the airdrop."
#                                 )
#        return ENTER_REFERRAL
#
#    Storage.updateParticipantComplete(update.message.from_user.id, referralCode)
#    hashedID = calculateRefferalCode(update.message.from_user.id)
#
#    img = open('100.webp', 'rb')
#    bot.send_sticker(chat_id=update.message.chat_id,
#                     sticker=img,
#                     reply_markup=ReplyKeyboardRemove())
#
#    update.message.reply_text("Received referral code is correct.\n"
#                             "It brings you and your friend " + str(BONUS) + "% more tokens.\n\n"
#                                                                              "Thank you for participation in the Iryo Airdrop campaign!\n\n"
#                                                                              "     🎯Your referral code: " + hashedID + "\n\n"
#                                                                                                                         "You can get additional IRYO tokens by sharing your referral code. "
#                                                                                                                         "Every user who successfully joins the airdrop will bring you 20% additional bonus tokens. "
#                                                                                                                         "The number of people using your referral code is only limited by the campaign itself\n\n"
#                                                                                                                         "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
#                                                                                                                        "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
#                             reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
#   return NO_STATE


#def referralGotError(bot, update):
#    receivedText = update.message.text
#    referralCode = receivedText.strip()
#    if Storage.isReferralTimeCorrect(update.message.from_user.id) == False:
#        hashedID = calculateRefferalCode(update.message.from_user.id)
#        Storage.updateParticipantComplete(update.message.from_user.id)
#
#        img = open('100.webp', 'rb')
#        bot.send_sticker(chat_id=update.message.chat_id,
#                         sticker=img,
#                         reply_markup=ReplyKeyboardRemove())
#
#        update.message.reply_text("Time to enter referral code of your friend is expired.\n\n"
#                                  "     🎯Your referral code: " + hashedID + "\n\n"
#                                                                             "You can get additional IRYO tokens by sharing your referral code. "
#                                                                             "Every user who successfully joins the airdrop will bring you 20% additional bonus tokens. "
#                                                                             "The number of people using your referral code is only limited by the campaign itself\n\n"
#                                                                             "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
#                                                                             "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
#                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
#
#        return NO_STATE
#
#    update.message.reply_text("Referral code is not correct or not found in database.\n\n"
#                              "   🎯Enter your friend's referral code now and you and your friend will receive 20% more tokens each! (Warning: You only have 15 minutes to do this!):\n\n"
#                              "    or\n\n"
#                              "   🎯Type or click /done to skip this step and finish the airdrop."
#                              )
#    return ENTER_REFERRAL
###########################################
def donebutton(bot, update):
    ##
    img = open('100.webp', 'rb')
    bot.send_sticker(chat_id=update.message.chat_id,
                     sticker=img,
                     reply_markup=ReplyKeyboardRemove())
    hashedID = calculateRefferalCode(update.message.from_user.id)
    Storage.updateParticipantComplete(update.message.from_user.id)
    update.message.reply_text("Thank you for participating in the Iryo Airdrop campaign!\n"
                                "Your address is correct and the pre-conditions are met.\n\n"
                                  "🎯 New referrals have been suspended!\n"
                                "Read why here: https://medium.com/p/4dfd238bf225\n\n"
                                  "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
                                 "And remember this is not Iryo’s final platform, you will need to register EOS address until ICO is be finished.",
                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE


def EOSaddressGot(bot, update):
    receivedText = update.message.text
    referralCode = receivedText.strip()

    if checkReferralCode(referralCode) == False or Storage.isReferralExists(referralCode) == False:
        update.message.reply_text("Referral code is not correct or not found in database.\n\n"
                                  "   🎯Enter your friend's referral code now and you and your friend will receive 20% more tokens each! (Warning: You only have 15 minutes to do this!):\n\n"
                                  "    or\n\n"
                                  "   🎯Type or click /done to skip this step and finish the airdrop."
                                 )
        return ENTER_EOS_ADDRESS

    Storage.updateParticipantComplete(update.message.from_user.id, referralCode)
    hashedID = calculateRefferalCode(update.message.from_user.id)

    img = open('100.webp', 'rb')
    bot.send_sticker(chat_id=update.message.chat_id,
                     sticker=img,
                     reply_markup=ReplyKeyboardRemove())

    update.message.reply_text("Received referral code is correct.\n"
                             "It brings you and your friend " + str(BONUS) + "% more tokens.\n\n"
                                                                              "Thank you for participation in the Iryo Airdrop campaign!\n\n"
                                                                              "     🎯Your referral code: " + hashedID + "\n\n"
                                                                                                                        "You can get additional IRYO tokens by sharing your referral code. "
                                                                                                                         "Every user who successfully joins the airdrop will bring you 20% additional bonus tokens. "
                                                                                                                         "The number of people using your referral code is only limited by the campaign itself\n\n"
                                                                                                                         "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
                                                                                                                        "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
                             reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
    return NO_STATE

###########################################

def participate(bot, update):
    if Storage.isUserExists(update.message.from_user.id):
        hashedID = calculateRefferalCode(update.message.from_user.id)
        update.message.reply_text("Your address or telegram ID already exists in database",
                                  #"     🎯Your referral code: " + hashedID + "\n\n"
                                  #                                           "You can get additional IRYO tokens by sharing your referral code. "
                                  #                                           "Every user who successfully joins the airdrop will bring you 20% additional bonus tokens. "
                                  #                                           "The number of people using your referral code is only limited by the campaign itself\n\n"
                                  #                                           "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
                                  #                                           "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE

    update.message.reply_text("To participate you’ll need to do 2 things:\n\n"

                              "🎯 Join the Iryo telegram group & the alerts channel.\n"
                              "		• https://t.me/IRYOnetwork - Iryo’s primary group - join the conversation!\n"
                              "		• https://t.me/iryo_alerts - An important channel managed by the Iryo team (security alerts, contract address, etc)\n\n"

                              "🎯Tell us your valid Ethereum address on which at least one of next two conditions are true on March 1st, 2018. Block 5174125 https://etherscan.io/block/5174125\n"
                              "		• At least 0.1 ETH on your address.\n"
                              "		• At least 1 EOS token on your address.\n\n"

                              "Please enter your Ethereum address (Warning: An address from an exchange will not work, i.e Binance, Kraken etc.)",
                              reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True),
                              disable_web_page_preview=True)
    return NO_STATE


def referralCode(bot, update):
    referral = Storage.getReferralLink(update.message.from_user.id)
    if (referral == ''):
        update.message.reply_text(
            "You are not in referral program!\n"
            "Join to Iryo Airdrop by pasting your Ethereum address.",
            reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE
    update.message.reply_text(
        "Your referral code:\n" +
        "   🎯" + referral + "\n\n"
                             "Keep sharing 🙌",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
    return NO_STATE


def referralCount(bot, update):
    referral = Storage.getReferralLink(update.message.from_user.id)
    if (referral == ''):
        update.message.reply_text(
            "Referrals have been suspended!\n"
            "Read why here: https://medium.com/p/4dfd238bf225",
            reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE
    count = Storage.getReferralCount(update.message.from_user.id)
    iWereInvited = False if Storage.getMyReferral(update.message.from_user.id) == '' else True
    if iWereInvited:
        count += 1
    update.message.reply_text("You have got " + str(count) + " referrals.\n"+
                                "That brings you " + str(count * BONUS) + "% more tokens.\n\n"+
                                "Referrals have been suspended!\n"+
                                "Read why here: https://medium.com/p/4dfd238bf225",
                                reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE


def info(bot, update):
    # reply_keyboard = [['/new', '/cancel', '/help']]
    update.message.reply_text(
        "Hi! I am Iryo Airdrop Bot, deployed by the Iryo team.\n"
        "My job is to get you some free Iryo tokens!\n"
        "I don’t want to bore you with the details, so go ahead and check out this walkthrough guide " + ARTICLE + " before interacting with me.!\n"
                                                                                                                   "To participate you’ll need to do 2 things:\n\n"

                                                                                                                   "🎯 Join the Iryo telegram group & the alerts channel.\n"
                                                                                                                   "		• https://t.me/IRYOnetwork - Iryo’s primary group - join the conversation!\n"
                                                                                                                   "		• https://t.me/iryo_alerts - An important channel managed by the Iryo team (security alerts, contract address, etc)\n\n"

                                                                                                                   "🎯Tell us your valid Ethereum address on which at least one of next two conditions are true on March 1st, 2018. Block 5174125 https://etherscan.io/block/5174125\n"
                                                                                                                   "		• At least 0.1 ETH on your address.\n"
                                                                                                                   "		• At least 1 EOS token on your address.\n\n"
        ,
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE

def eosAddress(bot, update):
    #temp code //no eos
    update.message.reply_text(
        "Registration of EOS address is disabled. \n    🎯Come back in in June.",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE


    #end of: jtemp code //no eos

    if Storage.isUserExists(update.message.from_user.id) == False:
        update.message.reply_text(
            "You are not registered in the Iryo Airdop.\nRegister to Airdrop, then come back to add EOS address.",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
        return NO_STATE

    eosAddress = Storage.isEOSAddressExists(update.message.from_user.id)
    if eosAddress != '':
        update.message.reply_text(
            "Your current registered EOS address is\n" + eosAddress + " \n\n"
            "   🎯Paste the new one to update\n"
            "    or\n"
            "   🎯Type or click /cancel to use other commands",
            reply_markup=ReplyKeyboardRemove(),
            disable_web_page_preview=True)
        return CHECK_EOS_ADDRESS

    update.message.reply_text(
            "Your haven't registered EOS address yet\n\n"
            "   🎯Paste the valid EOS address\n"
            "    or\n"
            "   🎯Type or click /cancel to use other commands.",
            reply_markup=ReplyKeyboardRemove())
    return CHECK_EOS_ADDRESS

def eosAddressReceived (bot, update):
    receivedText = update.message.text.strip()
    update.message.reply_text("Checking structure of EOS address ...")
    if checkEOSaddressStructure(receivedText) == False:
        update.message.reply_text(
            "Inserted EOS address is not correct or unknown command. \n\n"
            "   🎯Paste the valid EOS address\n"
            "    or\n"
            "   🎯Type or click /cancel to finish registration and provide to us EOS address later.")
        return ENTER_EOS_ADDRESS

    if Storage.isUserExists(update.message.from_user.id) == False:
        update.message.reply_text(
            "You are not registered in the Iryo Airdop. Register to Airdrop, then come back to add EOS address.",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
        return NO_STATE

    #update storage
    Storage.addEOSToMainUser(update.message.from_user.id, receivedText)

    img = open('100.webp', 'rb')
    bot.send_sticker(chat_id=update.message.chat_id,
                     sticker=img,
                     reply_markup=ReplyKeyboardRemove())

    update.message.reply_text("Thank you for participating in the Iryo Airdrop campaign!\n"
                                "Your ETH and EOS addresses are correct and the pre-conditions are met.\n\n"
                                  "🎯 New referrals have been suspended!\n"
                                "Read why here: https://medium.com/p/4dfd238bf225\n\n"
                                  "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
                                 "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE

def cancelEosProcedure(bot, update):
    img = open('100.webp', 'rb')
    bot.send_sticker(chat_id=update.message.chat_id,
                     sticker=img,
                     reply_markup=ReplyKeyboardRemove())
    update.message.reply_text("Thank you for participating in the Iryo Airdrop campaign!\n"
                              "Your ETH address is correct and the pre-conditions are met.\n\n"
                              "Please register your EOS address before ICO is finished -  button '"+ REGISTER_EOS_ADDRESS +"'.\n\n"
                              "🎯 New referrals have been suspended!\n"
                              "Read why here: https://medium.com/p/4dfd238bf225\n\n"
                              "You will receive  tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n"
                              "And remember this is not Iryo’s final platform, you will need to move them to EOS once the migration plan is revealed!",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE

#####check section
def eosAddressReceivedCheck (bot, update):
    receivedText = update.message.text.strip()
    update.message.reply_text("Checking structure of EOS address ...")
    if checkEOSaddressStructure(receivedText) == False:
        update.message.reply_text(
            "Inserted EOS address is not correct or unknown command. \n\n"
            "   🎯Paste the valid EOS address\n"
            "    or\n"
            "   🎯Type or click /cancel to finish registration and provide to us EOS address later.")
        return CHECK_EOS_ADDRESS

    if Storage.isUserExists(update.message.from_user.id) == False:
        update.message.reply_text(
            "You are not registered in the Iryo Airdop. Register to Airdrop, then come back to add EOS address.",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
        return NO_STATE

    #update storage
    Storage.addEOSToMainUser(update.message.from_user.id, receivedText)
    update.message.reply_text("Your EOS address has been updated\n\n"
                                "You will receive tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE

def cancelEosProcedureCheck(bot, update):
    update.message.reply_text("You haven't changed your EOS address.\n\n"
                                "You will receive tokens after the successful ICO. Keep your eyes pegged to the alerts channel!\n\n",
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE

def help(bot, update):
    update.message.reply_text(
        "Hi! I am Iryo Airdrop Bot, deployed by Iryo team.\n"
        "My job is to get you some free Iryo tokens in this Airdrop campaign. "
        "I don’t want to bore you with details, so please visit the explanation and justification " + ARTICLE + " on how the whole campaign would be run!  You will get the tokens after the ico is finished.\n\n"
                                                                                                                "Here are few additional commands you can use to talk with bot: \n\n" +
        '/info - Information about Iryo Airdrop\n'
        #'/code - Your referral code\n'
        '/bonus - Your received bonus\n'
        '/help - help about Iryo Airdrop Bot\n\n'
        'Your Telegram ID: ' + str(update.message.from_user.id) + '\n\n',
        reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True), disable_web_page_preview=True)
    return NO_STATE


def stat(bot, update):
    try:
        receivedText = update.message.text
        if SECRET not in receivedText:
            update.message.reply_text("Password/secret is incorrect!",
                                      reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
            return NO_STATE

        update.message.reply_text("Correct password! Retrieving data may take a few seconds",
                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))

        statistic = Storage.stat()
        output = "New participants grouped by date\n\n" \
                 "Date                |   New users (with referrals)\n"
        total = 0
        for item in statistic:
            output += (str(item) + "    |   " + str(statistic[item][0]) + " (" + str(statistic[item][1]) + ")\n")
            total += int(statistic[item][0])

        output += ("----------------------------------------\n")
        output += ("TOTAL:           |   " + str(total) + " participants!")

        update.message.reply_text(output,
                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE
    except:
        update.message.reply_text("Exception occured.",
                                  reply_markup=ReplyKeyboardMarkup(bot_keyboard, resize_keyboard=True))
        return NO_STATE


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      RegexHandler('^0x[a-fA-F0-9]{40}$', ethereumAddressReceived, pass_user_data=True),
                      CommandHandler('help', help),
                      CommandHandler('info', info),
                      CommandHandler('eosAddress', eosAddress),
                      #CommandHandler('code', referralCode),
                      CommandHandler('bonus', referralCount),
                      CommandHandler('stat', stat),
                      RegexHandler('^(' + PARTICIPATE + ')$', participate),
                      RegexHandler('^(' + INFO + ')$', info),
                      RegexHandler('^(' + REGISTER_EOS_ADDRESS + ')$', eosAddress),
                      #RegexHandler('^(' + REFERRAL_CODE + ')$', referralCode),
                      RegexHandler('^(' + YOUR_BONUS + ')$', referralCount),
                      RegexHandler('^(' + HELP + ')$', help),
                      MessageHandler(Filters.text, ethereumAddressReceived, pass_user_data=True),
                      ],

        states={
            NO_STATE: [RegexHandler('^0x[a-fA-F0-9]{40}$', ethereumAddressReceived, pass_user_data=True),
                       CommandHandler('help', help),
                       CommandHandler('info', info),
                       CommandHandler('eosAddress', eosAddress),
                       #CommandHandler('code', referralCode),
                       CommandHandler('bonus', referralCount),
                       CommandHandler('stat', stat),
                       CommandHandler('start', start),
                       RegexHandler('^(' + PARTICIPATE + ')$', participate),
                       RegexHandler('^(' + INFO + ')$', info),
                       RegexHandler('^(' + REGISTER_EOS_ADDRESS + ')$', eosAddress),
                       #RegexHandler('^(' + REFERRAL_CODE + ')$', referralCode),
                       RegexHandler('^(' + YOUR_BONUS + ')$', referralCount),
                       RegexHandler('^(' + HELP + ')$', help),
                       MessageHandler(Filters.text, ethereumAddressReceived, pass_user_data=True)
                       ],
            ENTER_EOS_ADDRESS: [MessageHandler(Filters.text, eosAddressReceived),
                       CommandHandler('cancel', cancelEosProcedure),
                       RegexHandler('^(cancel)$', cancelEosProcedure),
                       ],
            CHECK_EOS_ADDRESS: [MessageHandler(Filters.text, eosAddressReceivedCheck),
                                CommandHandler('cancel', cancelEosProcedureCheck),
                                RegexHandler('^(cancel)$', cancelEosProcedureCheck),
                                ],
            #not in use
            #ENTER_REFERRAL: [#CommandHandler('done', donebutton),
            #                 CommandHandler('help', referralGotError),
            #                 CommandHandler('info', referralGotError),
            #                 CommandHandler('code', referralGotError),
            #                 CommandHandler('bonus', referralGotError),
            #                 CommandHandler('stat', referralGotError),
            #                 CommandHandler('start', referralGotError),
            #                 RegexHandler('^(' + PARTICIPATE + ')$', referralGotError),
            #                 RegexHandler('^(' + INFO + ')$', referralGotError),
            #                 RegexHandler('^(' + REFERRAL_CODE + ')$', referralGotError),
            #                 RegexHandler('^(' + YOUR_BONUS + ')$', referralGotError),
            #                 RegexHandler('^(' + HELP + ')$', referralGotError),
            #                MessageHandler(Filters.text, referralGot)
            #                ],
        },

        fallbacks=[RegexHandler('^something$', info, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)
    # log all errors
    dp.add_error_handler(error)
    updater.start_polling(poll_interval=0.0,
                          timeout=10,
                          network_delay=5.,
                          clean=False,
                          bootstrap_retries=0)
    updater.idle()


if __name__ == '__main__':
    main()
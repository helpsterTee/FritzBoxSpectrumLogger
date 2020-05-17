from bs4 import BeautifulSoup
import requests
import hashlib
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from datetime import datetime
import time

# assorted vars
baseurl = "http://fritz.box/"
lua_login = "login_sid.lua"
lua_spectrum = "internet/dsl_spectrum.lua"
max_bit_display = 16 # scale to maximum 24 bits
max_snr_display = 70 # scale to maximum 70 dB

# timer settings
timer_interval = 5 * 60 # run every 5 minutes

# FritzBox login credentials
username = "username"
password = "password"


### PLEASE DISPERSE, THERE IS NOTHING TO SEE HERE ###
def calculate_spectrum(data):
    jdata = json.loads(data)

    # get maximum bin count
    maxlen = len(jdata["port"][0]["us"]["ACT_BIT_VALUES"])
    maxlen_snr = len(jdata["port"][0]["us"]["ACT_SNR_VALUES"])

    # graph creation
    act_bit = np.array(jdata["port"][0]["us"]["ACT_BIT_VALUES"])
    act_snr = np.array(jdata["port"][0]["us"]["ACT_SNR_VALUES"])
    pilot_line = jdata["port"][0]["us"]["PILOT_VALUES"][0]

    tones_per_bin = float(jdata["port"][0]["us"]["TONES_PER_BAT_VALUE"])
    tones_per_snr = float(jdata["port"][0]["us"]["TONES_PER_SNR_VALUE"])
    hz_per_bin = float(jdata["port"][0]["us"]["MAX_BAT_FREQ"]) / maxlen / 100
    hz_per_snr = float(jdata["port"][0]["us"]["MAX_SNR_FREQ"]) / maxlen / 100
    width = 1

    # band coloring
    colors = np.empty(maxlen, dtype='str')
    colors[:maxlen] = "b"
    bands = jdata["port"][0]["us"]["BIT_BANDCONFIG"]
    for band in bands:
        colors[band["FIRST"]:band["LAST"]] = "g"

    # define bins
    x_values = np.arange(maxlen)
    x_values_snr = np.arange(maxlen_snr)

    # scale snr
    act_snr = act_snr * 0.5

    # create multiple plots
    fig, ax = plt.subplots(2, 1)

    ### FIRST PLOT - BIT DISPLAY
    # create plot
    rects1 = ax[0].bar(x_values, act_bit, width, color=colors.tolist())

    # set main axis
    ax[0].set_title("Bit Values")
    ax[0].set_ylabel("Bits")
    ax[0].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:0.1f}'.format(x*tones_per_bin)))
    ax[0].set_xlabel("Tones")
    ax[0].set_xlim([0, maxlen])
    ax[0].set_ylim([0, max_bit_display])

    # set frequency axis
    ax2 = ax[0].twiny()
    ax2.set_xlim(ax[0].get_xlim())
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:0.1f}'.format(x*hz_per_bin)))
    ax2.set_xlabel("KHz")

    # layout
    fig.tight_layout()

    ### SECOND PLOT - SNR
    rects2 = ax[1].bar(x_values_snr, act_snr, width, color="y")

    # set main axis
    ax[1].set_title("SNR Values")
    ax[1].set_ylabel("dB")
    ax[1].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:0.1f}'.format(x*tones_per_snr)))
    ax[1].set_xlabel("Tones")
    ax[1].set_xlim([0, maxlen_snr])
    ax[1].set_ylim([0, max_snr_display])

    # set frequency axis
    ax2 = ax[1].twiny()
    ax2.set_xlim(ax[1].get_xlim())
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:0.1f}'.format(x*hz_per_bin)))
    ax2.set_xlabel("KHz")

    # plot pilot tone
    ax[0].axvline(pilot_line, color="r")

    # plot
    plt.subplots_adjust(hspace=1)

    # add time
    now = datetime.now()
    datestring = now.strftime("%d.%m.%Y - %H:%M:%S")
    plt.figtext(0.1, 0.5, datestring)

    # save
    timestamp = int(datetime.timestamp(now))
    fig.savefig('./output/'+str(timestamp)+".png", dpi=200)

# main loop
starttime = time.time()
while (True):
    # get session challenge
    r_url = baseurl + lua_login
    r_resp = requests.get(r_url)

    # parse challenge request
    tree = BeautifulSoup(r_resp.text, "xml")
    challenge = tree.SessionInfo.Challenge.string
    m = hashlib.md5()
    c_request = challenge+"-"+password
    m.update(c_request.encode('utf-16le'))
    c_response_hash = m.hexdigest()
    c_response = challenge + "-" + c_response_hash
    c_response_url = r_url+'?response='+c_response
    r_resp = requests.get(r_url+'?username='+username+'&response='+c_response)

    tree = BeautifulSoup(r_resp.text, "xml")
    sid = tree.SessionInfo.SID.string

    if sid == '0000000000000000':
        print("["+datetime.now().isoformat() + "] Login failed")
    else:
        print("["+datetime.now().isoformat() + "] Login success")

        s_url = baseurl + lua_spectrum + '?sid=' + sid + '&no_sidrenew=1&myXhr=1&useajax=1&xhr=1'
        s_resp = requests.get(s_url)

        # do the magic
        calculate_spectrum(s_resp.text)

        #logout at end
        r_resp = requests.get(r_url+'?logout=1&sid='+sid)

    # loop delay
    time.sleep(timer_interval - ((time.time() - starttime) % timer_interval))

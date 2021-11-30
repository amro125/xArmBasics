from rtpmidi import RtpMidi
from pymidi import server
import os
import sys
import time
import csv
import pdb
from queue import Queue
from threading import Thread
import time


def cvt(path):
    return_vector = []
    for i in range(7 * len(arms)):
        return_vector.append(float(path[i]))
    return return_vector


def playDance(step):
    length = len(step)
    # for a in range (3):
    #     print(2-a)
    #     time.sleep(1)
    for i in range(length):
        start_time = time.time()
        # board.digital[4].mode = pyfirmata.INPUT
        # board.digital[2].mode = pyfirmata.INPUT
        # red = board.digital[4].read()

        j_angles = (step[i])
        # b=6
        # arms[b].set_servo_angle_j(angles=j_angles[(b * 7):((b + 1) * 7)], is_radian=False)

        for b in range(totalArms):
             arms[b].set_servo_angle_j(angles=j_angles[(b * 7):((b + 1) * 7)], is_radian=False)
        tts = time.time() - start_time
        sleep = 0.006 - tts

        if tts > 0.006:
            sleep = 0

        #print(i*0.006)
        time.sleep(sleep)


def readFile(csvFile):
    flower = []
    with open(csvFile, newline='') as csvfile:
        paths_reader_j = csv.reader(csvfile, delimiter=',', quotechar='|')
        for path in paths_reader_j:
            flower.append(cvt(path))
    return flower


def setup():
    for a in arms:
        a.set_simulation_robot(on_off=False)
        #a.motion_enable(enable=True)
        a.clean_warn()
        a.clean_error()
        a.set_mode(0)
        a.set_state(0)
        a.set_servo_angle(angle=[0.0, 0.0, 0.0, 1.57, 0.0, 0, 0.0], wait=False, speed=0.4, acceleration=0.25,
                          is_radian=True)
#1.57

class MyHandler(server.Handler):
    def on_peer_connected(self, peer):
        # Handler for peer connected
        print('Peer connected: {}'.format(peer))


    def on_peer_disconnected(self, peer):
        # Handler for peer disconnected
        print('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        # Handler for midi msgs
        for command in command_list:
            chn = command.channel

            if chn == 13:  # this means its channel 14!!!!!
                if command.command == 'note_on':
                    print(chn)
                    key = command.params.key.__int__()
                    velocity = command.params.velocity
                    print('key {} with velocity {}'.format(key, velocity))
                    q.put(velocity)


                    #playDance(dances[velocity])


if __name__ == "__main__":
    ROBOT = "xArms"
    PORT = 5004

    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

    from xarm.wrapper import XArmAPI

    arm1 = XArmAPI('192.168.1.208')
    arm2 = XArmAPI('192.168.1.244')
    arm3 = XArmAPI('192.168.1.203')
    arm4 = XArmAPI('192.168.1.236')
    arm5 = XArmAPI('192.168.1.226')
    arm6 = XArmAPI('192.168.1.242')
    arm7 = XArmAPI('192.168.1.215')
    arm8 = XArmAPI('192.168.1.234')
    arm9 = XArmAPI('192.168.1.237')
    arm10 = XArmAPI('192.168.1.204')


    arms = [arm1, arm2, arm3, arm4, arm5, arm6, arm7, arm8, arm9, arm10]
    totalArms = len(arms)


    directory = '/home/codmusic/Desktop/xArmTrajectories2/'
    dances = []
    trajectories = sorted(os.listdir(directory))
    for filename in trajectories:
        if filename.endswith(".csv"):
            print(filename)
            currentDance = (readFile(os.path.join(directory, filename)))
            dances.append(currentDance)
            continue

    setup()
    repeat = input("do we need to repeat? [y/n]")
    if repeat == 'y':
        setup()
    for a in arms:
        a.set_mode(1)
        a.set_state(0)


    def producer(out_q):
        while True:
            # Produce some data
            data = input("type a number")
            out_q.put(data)


    # A thread that consumes data
    def consumer(in_q):
        while True:
            # Get some data
            velocity = in_q.get()
            # Process the data
            print('playing dance #', velocity)
            playDance(dances[velocity-1])

    


    # Create the shared queue and launch both threads
    q = Queue()

    t2 = Thread(target=consumer, args=(q,))
    t2.start()
    rtp_midi = RtpMidi(ROBOT, MyHandler(), PORT)
    rtp_midi.run()


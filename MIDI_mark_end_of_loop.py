#from mido import MidiFile, Message
import mido
from tkinter import *
from tkinter import filedialog as fd
import os
#import math
dir(Message)
CC_NOTE_OFF_DISACTIVATED = 123
note_off_active == True
TICKS_PER_BEAT = 960
kontakt_listener_resolution = 16 # = 0.25 / (960 / 16) 
kontakt_ticks_for_listcall = TICKS_PER_BEAT / kontakt_listener_resolution

folderIN = ""
folderOUT = ""
filesIn = []

suffices = ["C0","C#0","D0","D#0","E0","F0","F#0","G0","G#0","A0","A#0","B0",
			"C1","C#1","D1","D#1","E1","F1","F#1","G1","G#1","A1","A#1","B1",
			"C2","C#2","D2","D#2","E2","F2","F#2","G2","G#2","A2","A#2","B2",
			"C3","C#3","D3","D#3","E3","F3","F#3","G3","G#3","A3","A#3","B3",
			"C4","C#4","D4","D#4","E4","F4","F#4","G4","G#4","A4","A#4","B4",
			"C5","C#5","D5","D#5","E5","F5","F#5","G5","G#5","A5","A#5","B5",
			"C6","C#6","D6","D#6","E6","F6","F#6","G6","G#6","A6","A#6","B6",
			"C7","C#7","D7","D#7","E7","F7","F#7","G7","G#7","A7","A#7","B7",
			"C8","C#8","D8","D#8","E8","F8","F#8"]

root = Tk()
root.geometry("500x200")
root.title("")

def sel_folderIN():
	global folderIN
	global folderOUT
	folderIN = fd.askdirectory()
	print("Import Folder: ", folderIN)

	Label_FoldIN.config(text=folderIN)
	if folderOUT == "":
		folderOUT = folderIN
	Label_FoldOUT.config(text=folderOUT)

def sel_folderOUT():
	global folderOUT
	global folderIN
	folderOUT = fd.askdirectory()
	print("Export Folder: ", folderOUT)
	Label_FoldOUT.config(text=folderOUT)
	if folderIN == "":
		folderIN = folderOUT
	Label_FoldIN.config(text=folderIN)

def run():
	check_batch_folder()

	if len(filesIn) > 0:
		""" UI """
		if int(Spbx_offsetFrom.get()) > int(Spbx_offsetTo.get()):
			offsetFr = int(Spbx_offsetTo.get())
			offsetTo = int(Spbx_offsetFrom.get())
		else:
			offsetFr = int(Spbx_offsetFrom.get())
			offsetTo = int(Spbx_offsetTo.get())

		
		# ~~~ parse imported midi files
		for fIn in filesIn:
			fOut = fIn[0:-4] + "_edit.MID"
			print("file in is: ", fIn)
			print("file out is: ", fOut)
			# ~~~ edit imported midi file
			midIn = mido.MidiFile(folderIN + "/" + fIn, clip=True)
			midIn_dur = midIn.length # in beats
			print(f"file duration in beats: {midIn.length}")
			file_length_tick = round(midIn.length) * 960 
			print(f"file duration in ticks: {file_length_tick}")
			marker_pos_tick = file_length_tick - (kontakt_ticks_for_listcall / 2)
			midOut = mido.MidiFile()
			for track in midIn.tracks:
				edited_track = []
				track_abs_ticks = [[],[],[]] # [0]type, [1]value, [2]abs time in ticks
				#print(track)
				last_event_tick = 0
				event_counter = 0
				cc_added = False
				note_to_end_file = False
				print("n events in track: ", len(track))
				for msg in track:
					print(f"MSG: {msg}")
					if msg.type == 'note_on' or msg.type == 'note_off':
						#print(msg)
						
						msg.time = int(msg.time/2)
						last_event_tick += msg.time
						msg.note = msg.note
						track_abs_ticks[0].append(msg.type)
						track_abs_ticks[1].append(msg.note)
						track_abs_ticks[2].append(last_event_tick)
						print(f"last event tick: {last_event_tick} , beat: {last_event_tick/TICKS_PER_BEAT}, file pos: {last_event_tick/file_length_tick}")
						#print("note: ", msg.note, ", time: " , msg.time, ", pos: " , msg.pos)
						#if last_event_tick < file_length_tick - (960 / 32):
						edited_track.append(msg)
						#msg = Message('note_on', note=60)
					else:
						if msg.type =='control_change':
							print(f"Control change: {msg}")
							msg.time = int(msg.time/2)
							last_event_tick += msg.time
							track_abs_ticks[0].append(msg.type)
							track_abs_ticks[1].append(msg.control)
							track_abs_ticks[2].append(last_event_tick)
							if msg.control == CC_NOTE_OFF_DISACTIVATED:
								note_off_active == False
							print(f"last event tick: {last_event_tick} , beat: {last_event_tick/TICKS_PER_BEAT}, file pos: {last_event_tick/file_length_tick}")

						if msg.type =='end_of_track':
							edited_track.append(msg)
							print(f"End of Track: {msg}")
				print("<<<<<<< SUMMARY: ")
				idx_marker = None
				for i in range(len(track_abs_ticks[0])):
					print(f"idx: {i} , type: {track_abs_ticks[0][i]}, note/ch: {track_abs_ticks[1][i]}, abs time: {track_abs_ticks[2][i]}") 
					if track_abs_ticks[2][i] == file_length_tick: 
						print("THIS IS AFTER THE MARKER")
						if not note_to_end_file:
							note_to_end_file == True

				if note_to_end_file:
					msg = ('control_change', channel=0, control=123, value=64, time=0) 
					edited_track.append(msg)
				else: msg = ('control_change', channel=0, control=123, value=64, time=file_length_tick + last_event_tick)
						
				
							
						
				print("EDITED TRACK: ")
				print(edited_track)
				"""
				delta_time =   int(960 / 32) #int(file_length_tick - last_event_tick - (960 / 32)  / 2)
				print("CC event delta tick: ", delta_time)
				edited_track.append(mido.Message('control_change', channel = cc['channel'], control= cc['control'], value= 127, time=delta_time))
				delta_time = 10
				edited_track.append(mido.Message('control_change', channel = cc['channel'], control= cc['control'], value= 0, time=delta_time))
				cc_added = True
				"""


				track.clear()
				track.extend(edited_track)
				
				midOut.tracks.append(edited_track)

			#midOut.save(folderOUT + "/" + fOut)
	else:
			print("ERROR: NO SOURCE MIDI FILES FOUND")

def check_batch_folder():
	global filesIn
	filesIn = []
	files = os.listdir(folderIN)
	for f in files:
		if f.lower().endswith('.mid'):
			filesIn.append(f)
			print("FOUND FILE IN FOLDER: ",f)
			midIn = mido.MidiFile(folderIN + "/" + f, clip=True)
			print(f"file duration: {midIn.length}")


root.columnconfigure(0, weight=10)
root.columnconfigure(1, weight=30)
root.columnconfigure(2, weight=10)

root.rowconfigure(0, weight=10)
root.rowconfigure(1, weight=20)
root.rowconfigure(2, weight=10)
root.rowconfigure(3, weight=10)
root.rowconfigure(4, weight=10)

Button_FoldIN = Button(root, height=2, width = 30, text="Import Folder", command=lambda: sel_folderIN())
Button_FoldIN.grid(row = 0, column = 0, padx=10,pady = 10)
Label_FoldIN = Label(root, text="NO FOLDER SELECTED",height = 1, width = 30)
Label_FoldIN.grid(row = 1, column = 0, sticky = N, padx=10,pady = 10)

Button_FoldOUT = Button(root, height=2, width=30, text="Export Folder", command=lambda: sel_folderOUT())
Button_FoldOUT.grid(row = 0, column = 2, padx=10,pady = 10)
Label_FoldOUT = Label(root, text="NO FOLDER SELECTED",height = 1, width = 30)
Label_FoldOUT.grid(row = 1, column = 2, sticky = N, padx=10,pady = 10)

Spbx_offsetFrom = Spinbox(root, width=10,from_= -127, to = 127)
Spbx_offsetFrom.grid(row = 2, column = 0, padx=10,pady = 10)

Label_To = Label(root, text="to",height = 1, width = 10)
Label_To.grid(row = 2, column = 1)

Spbx_offsetTo = Spinbox(root, width=10,from_= -127, to = 127)
Spbx_offsetTo.grid(row = 2, column = 2, padx=10,pady = 10)

Button_Run = Button(root, height = 1, width = 20, text ="RUN", command = lambda:run())
Button_Run.grid(row = 3, column = 0, columnspan=3, rowspan=2,padx=10,pady = 10)

root.mainloop()
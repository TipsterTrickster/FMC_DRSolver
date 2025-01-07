import subprocess
from subprocess import Popen, PIPE
import re
from itertools import groupby
import csv

# Configuration
nissy_path = "/usr/local/bin"
nissy_filename = "nissy"

preset = int(input("Preset (0 CUSTOM): "))


if preset == 0:
    eoLength = int(input("EO Length: "))
    drLength = int(input("DR Length: "))
    solutionLength = int(input("Solution Length: "))
    niss = input("NISS -N (1)  or -L (0): ")
    if niss == 1:
        Niss = "-N"
    else:
        Niss = "-L"
    maxEO = int(input("max eo: "))
elif preset == 1:
    eoLength = 5
    drLength = 11
    htrLenth = 15
    solutionLength = 21
    sliceSLenth = 22
    Niss = "-N"
    maxEO = 3
elif preset == 2:
    eoLength = 5
    drLength = 12
    solutionLength = 22
    Niss = "-L"
    maxEO = 3


scramble = input("Enter Scramble: ")

# Functions
def variations(inputList):
    lst = []
    for item in inputList:
        length = item[1]
        moves = item[0]
        reg = re.split(r'\(|\)', moves)[0].strip()
        lst.append((moves, length))
        if "(" in moves:
            inv = re.split(r'\(|\)', moves)[-2]
            
            if reg == '':
                lst.append((f"({inv}')", length))
                if inv[-3:] == "F B" or inv[-3:] == "U D" or inv[-3:] == "R L":
                    lst.append((f"({inv[:-2]}'{inv[-2:]})", length))
                    lst.append((f"({inv[:-2]}'{inv[-2:]}')", length))
            else:
                lst.append((f"{reg} ({inv}')", length))
                lst.append((f"{reg}' ({inv}')", length))
                lst.append((f"{reg}' ({inv})", length))
                if inv[-3:] == "F B" or inv[-3:] == "U D" or inv[-3:] == "R L":
                    lst.append((f"{reg} ({inv[:-2]}'{inv[-2:]})", length))
                    lst.append((f"{reg} ({inv[:-2]}'{inv[-2:]}')", length))
                    lst.append((f"{reg}' ({inv[:-2]}'{inv[-2:]})", length))
                    lst.append((f"{reg}' ({inv[:-2]}'{inv[-2:]}')", length))
                    if reg[-3:] == "F B" or reg[-3:] == "U D" or reg[-3:] == "R L":
                        lst.append((f"{reg[:-2]}'{reg[-2:]} ({inv[:-2]}{inv[-2:]})", length))
                        lst.append((f"{reg[:-2]}'{reg[-2:]} ({inv[:-2]}{inv[-2:]}')", length))
                        lst.append((f"{reg[:-2]}'{reg[-2:]} ({inv[:-2]}'{inv[-2:]})", length))
                        lst.append((f"{reg[:-2]}'{reg[-2:]} ({inv[:-2]}'{inv[-2:]}')", length))
                        lst.append((f"{reg[:-2]}'{reg[-2:]}' ({inv[:-2]}{inv[-2:]})", length))
                        lst.append((f"{reg[:-2]}'{reg[-2:]}' ({inv[:-2]}{inv[-2:]}')", length))
                        lst.append((f"{reg[:-2]}'{reg[-2:]}' ({inv[:-2]}'{inv[-2:]})", length))
                        lst.append((f"{reg[:-2]}'{reg[-2:]}' ({inv[:-2]}'{inv[-2:]}')", length))
                elif reg[-3:] == "F B" or reg[-3:] == "U D" or reg[-3:] == "R L":
                    lst.append((f"{reg[:-2]}'{reg[-2:]} ({inv[:-2]}{inv[-2:]})", length))
                    lst.append((f"{reg[:-2]}'{reg[-2:]} ({inv[:-2]}{inv[-2:]}')", length))
                    lst.append((f"{reg[:-2]}'{reg[-2:]}' ({inv[:-2]}{inv[-2:]})", length))
                    lst.append((f"{reg[:-2]}'{reg[-2:]}' ({inv[:-2]}{inv[-2:]}')", length))
        else:
            lst.append((f"{reg}'", length))
            if reg[-3:] == "F B" or reg[-3:] == "U D" or reg[-3:] == "R L":
                lst.append((f"{reg[:-2]}'{reg[-2:]}", length))
                lst.append((f"{reg[:-2]}'{reg[-2:]}'", length))
    return lst

def EOSolver(scram):

    scrambleString = f'solve eo -t 7 -M {eoLength} -N {scram}'
    p = subprocess.Popen(nissy_filename, shell = True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,)

    nOutput = p.communicate(input=bytes(scrambleString,'utf-8'))
    nOutput = nOutput[0].decode()
    nOutput = re.split(r'nissy-# |\n|\r\n', nOutput)
    nOutput.pop(0)
    nOutput.pop()
    nOutput.pop()
    eos = []
    for eo in nOutput:
        eos.append((eo[:-4], int(eo[-2])))
    p.kill()

    return eos

def DRSolver(scram, eos):
    drs = []
    grouped_eos = [list(group) for key, group in groupby(eos, key=lambda x: x[1])]
    for geos in grouped_eos:
        eolen = max(geos[0][1], maxEO)
        scrambleList = [f'\n{scram} {eo[0]}' for eo in geos]

        scrambleString = f'solve dr-eo -i -t 8 -M {drLength - eolen} {Niss}' + ' '.join(scrambleList) + '\n'
        p = subprocess.Popen(nissy_filename, shell = True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,)
        nOutput = p.communicate(input=bytes(scrambleString,'utf-8'))


        nOutput = nOutput[0].decode()
        nOutput = re.split(">>> Line: |nissy-# ", nOutput)
        nOutput.pop(0)
        nOutput.pop(0)
        nOutput.pop()
        
        p.kill()
        
        for eo, ln in zip(geos, nOutput):
            nln = []
            ln = re.split(r"\n|\r\n", ln)
            ln.pop(0)
            ln.pop()        
            if len(ln) == 0:
                continue
            for l in ln:
                try:
                    nln.append((l[:-5], int(l[-3:-1])))
                except:
                    nln.append((l[:-4], int(l[-2])))
            nln = variations(nln)
            for l in nln:
                drs.append((eo[0] + ' ' + l[0], eo[1] + int(l[1])))
    return drs
        
def DRFINSolver(scram, drs):
    fins = []
    sorted_list = sorted(drs, key=lambda x: x[1])
    grouped_drs = [list(group) for key, group in groupby(sorted_list, key=lambda x: x[1])]
    for gdrs in grouped_drs:
        drlen = gdrs[0][1]
        scrambleList = [f'\n{scram} {dr[0]}' for dr in gdrs]
        scrambleString = f'solve drfin -i -t 8 -M {solutionLength - drlen}' + ' '.join(scrambleList) + '\n'
        p = subprocess.Popen(nissy_filename, shell = True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,)
        nOutput = p.communicate(input=bytes(scrambleString,'utf-8'))
        nOutput = nOutput[0].decode()
        nOutput = re.split(">>> Line: |nissy-# ", nOutput)
        nOutput.pop(0)
        nOutput.pop(0)
        nOutput.pop()
        p.kill()
        for dr, ln in zip(gdrs, nOutput):
            nln = []
            ln = re.split(r"\n|\r\n", ln)
            ln.pop(0)
            ln.pop()    
            if len(ln) == 0:
                continue

            for l in ln:
                try:
                    nln.append((l[:-5], int(l[-3:-1])))
                except:
                    nln.append((l[:-4], int(l[-2])))

            for l in nln:
                fins.append((dr[0] + ' ' + l[0], dr[1] + int(l[1])))
    return fins

def DRSLICESolver(scram, drs):
    fins = []
    sorted_list = sorted(drs, key=lambda x: x[1])
    grouped_drs = [list(group) for key, group in groupby(sorted_list, key=lambda x: x[1])]
    for gdrs in grouped_drs:
        drlen = gdrs[0][1]
        scrambleList = [f'\n{scram} {dr[0]}' for dr in gdrs]
        scrambleString = f'solve drslice -i -t 8 -M {sliceSLenth - drlen}' + ' '.join(scrambleList) + '\n'
        p = subprocess.Popen(nissy_filename, shell = True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,)
        nOutput = p.communicate(input=bytes(scrambleString,'utf-8'))
        nOutput = nOutput[0].decode()
        nOutput = re.split(">>> Line: |nissy-# ", nOutput)
        nOutput.pop(0)
        nOutput.pop(0)
        nOutput.pop()
        p.kill()
        for dr, ln in zip(gdrs, nOutput):
            nln = []
            ln = re.split(r"\n|\r\n", ln)
            ln.pop(0)
            ln.pop()    
            if len(ln) == 0:
                continue

            for l in ln:
                try:
                    nln.append((l[:-5], int(l[-3:-1])))
                except:
                    nln.append((l[:-4], int(l[-2])))

            for l in nln:
                fins.append((dr[0] + ' ' + l[0], dr[1] + int(l[1])))
    return fins

def HTRSolver(scram, eos):
    drs = []
    grouped_eos = [list(group) for key, group in groupby(eos, key=lambda x: x[1])]
    for geos in grouped_eos:
        eolen = max(geos[0][1], 7)
        scrambleList = [f'\n{scram} {eo[0]}' for eo in geos]
        scrambleString = f'solve htr -i -t 8 -M {htrLenth - eolen} {Niss}' + ' '.join(scrambleList) + '\n'
        p = subprocess.Popen(nissy_filename, shell = True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,)
        nOutput = p.communicate(input=bytes(scrambleString,'utf-8'))
        nOutput = nOutput[0].decode()
        nOutput = re.split(">>> Line: |nissy-# ", nOutput)
        nOutput.pop(0)
        nOutput.pop(0)
        nOutput.pop()
        p.kill()
        for eo, ln in zip(geos, nOutput):
            nln = []
            ln = re.split(r"\n|\r\n", ln)
            ln.pop(0)
            ln.pop()        
            if len(ln) == 0:
                continue
            for l in ln:
                try:
                    nln.append((l[:-5], int(l[-3:-1])))
                except:
                    nln.append((l[:-4], int(l[-2])))
            nln = variations(nln)
            for l in nln:
                drs.append((eo[0] + ' ' + l[0], eo[1] + int(l[1])))
    return drs



e = EOSolver(scramble)
eos = variations(e)

print(f"found {len(e)} EOs")

drs = DRSolver(scramble, eos)

print(f"found {len(drs)} DRs")

sols = []
sols_unfiltered = DRFINSolver(scramble, drs)

for solution in sols_unfiltered:
    last_move = ""
    filter_flag = 0
    for move in solution[0].split():
        if move == last_move:
            filter_flag = 1
            break
        else:
            last_move = move.rstrip("\'2")
    if filter_flag == 0:
        sols.append(solution)
    else:
        filter_flag = 0
    
        

min_movecount = min(item[1] for item in sols)

print(f"Solution Length: {min_movecount}")

for solution in sols:
    if solution[1] == min_movecount:
        print(solution[0])

with open("solutions.csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(sorted(sols, key=lambda x: x[1]))

with open("drs.csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(sorted(drs, key=lambda x: x[1]))

with open("eos.csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(sorted(e, key=lambda x: x[1]))
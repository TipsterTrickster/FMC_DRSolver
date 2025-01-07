import subprocess
from subprocess import Popen, PIPE
import re
from itertools import groupby
import csv

# Configuration


preset = int(input("Preset: "))

NISS = "-N"

if preset == 0:
    eoLength = int(input("EO Length: "))
    solutionLength = int(input("Solution Length: "))
elif preset == 1:
    eoLength = 5
    solutionLength = 20



nissy_path = "D:\\Users\\tipst\\OneDrive\\Desktop\\nissy"
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
    with subprocess.Popen("nissy.exe", shell = True, cwd = nissy_path,stdout=subprocess.PIPE,stdin=subprocess.PIPE) as p:
        scrambleString = f'solve eo -t 7 -M {eoLength} -N {scram}'
        nOutput = p.communicate(input=bytes(scrambleString,'utf-8'))
        nOutput = nOutput[0].decode()
        nOutput = re.split(r'nissy-# |\r\n', nOutput)
        nOutput.pop(0)
        nOutput.pop()
        nOutput.pop()
        eos = []
        for eo in nOutput:
            eos.append((eo[:-4], int(eo[-2])))
    return eos

def FINSolver(scram, eos):
    drs = []
    grouped_eos = [list(group) for key, group in groupby(eos, key=lambda x: x[1])]
    for geos in grouped_eos:
        eolen = max(geos[0][1], 3)
        scrambleList = [f'\n{scram} {eo[0]}' for eo in geos]
        with subprocess.Popen("nissy.exe", shell = True, cwd = nissy_path,stdout=subprocess.PIPE,stdin=subprocess.PIPE) as p:
            scrambleString = f'solve eofin -i -t 8 -M {solutionLength - eolen}' + ' '.join(scrambleList) + '\n'
            nOutput = p.communicate(input=bytes(scrambleString,'utf-8'))
            nOutput = nOutput[0].decode()
            nOutput = re.split(">>> Line: |nissy-# ", nOutput)
            nOutput.pop(0)
            nOutput.pop(0)
            nOutput.pop()
        for eo, ln in zip(geos, nOutput):
            nln = []
            ln = ln.split("\r\n")
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
                drs.append((eo[0] + ' ' + l[0], eo[1] + int(l[1])))
    return drs
       


e = EOSolver(scramble)
eos = variations(e)

print(f"found {len(e)} EOs")

sols = FINSolver(scramble, eos)

min_movecount = min(item[1] for item in sols)

print(f"Solution Length: {min_movecount}")

for solution in sols:
    if solution[1] == min_movecount:
        print(solution[0])
#####################################################################################
# Program: cirq_qkd.py
# Goal: This software implements the BB84 QKD protocol, simulating key agreement 
#	and eavesdropper interception attempts on ideal and noisy quantum channels.
# Date: 7th of May 2026  
# Ver: 1.6
# Author: Marco Mattiucci
#
# WARNING:
# It's strongly discouraged to install complex Python packages 
# like CirQ system-wide. Create an isolated environment:
# Create the directory:
# $ mkdir mycirq
# $ cd mycirq
# Install venv:
# $ sudo apt update
# $ sudo apt install python3-venv
# Verify owner:
# $ ls -ld .
# if owner is root:
# $ sudo chown -R $USER:$USER .
# Create the virtual environment (venv):
# $ python3 -m venv .venv
# Activate the venv:
# $ source .venv/bin/activate
# Upgrade pip and install CirQ:
# $ pip install --upgrade pip
# $ pip install cirq
#####################################################################################
# MIT License
#
# Copyright (c) 2026 Marco Mattiucci
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#####################################################################################




import cirq
import random
import hashlib
import math

# Procedure to obtain a SHA256 hash from a list of binary integers:
def myhash(binary_list):	
	return hashlib.sha256(str(binary_list).encode('utf-8')).hexdigest()

# Procedure for obtaining the n-th triangular sublist from a given list L:
def get_sublist(L, n):
	if n == 0: return L
	r = math.floor((-1 + math.sqrt(1 + 8 * n)) / 2)
	T_r = (r * (r + 1)) // 2
	start = n - T_r
	end_offset = r - start
	end = len(L) - end_offset
	return L[start:end]

# Function to check if input is a real (float) number:
def is_a_real_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    




####################################
# Variable Initialization Section: #
####################################
Q__channel = cirq.NamedQubit("Q__channel") # Main quantum communication channel
QRNGalice1 = cirq.NamedQubit("QRNGalice1") # Quantum channel 1 for QRNG1 (Alice random key)
QRNGalice2 = cirq.NamedQubit("QRNGalice2") # Quantum channel 2 for QRNG2 (Alice random base)
QRNGbob__1 = cirq.NamedQubit("QRNGbob__1") # Quantum channel 3 for QRNG3 (Bob random base)

bob_errors = 0	# Nr of wrong bits received by Bob
eve_errors = 0	# Nr of wrong bits received by Eve (eavesdropper)
bob_key_bit_counter = 0	# Nr of bits received by Bod
eve_intercepted_bit_counter = 0	# Nr of bits intercepted by Eve
alice_random_bit_list = []	# List of bits issued by QRNG1 for Alice (includes the shared key)
alice_key_bit_list = []		# List of bits selected by Alice for common base with Bob
alice_random_base_list = []	# List of quantum random bases used by Alice
alice_matching_bases_positions = []	# List of the bit positions where Alice's and Bob's bases match
bob_key_bit_list = []		# List of bits selected by Bob where his basis matches Alice’s
bob_random_base_list = []	# List of quantum random bases used by Bob
bob_received_bit_list = []	# List of bits measured by Bod in the quantum channel
bob_received_bad_bit_list = []	# List of bad bits selected by Bob where his basis matches Alice’s
eve_key_bit_list = []		# List of bits selected by Eve for common base with Alice
eve_pseudo_random_base_list = []	# List of pseudo-random bases used by Eve
eve_intercepted_bit_list = []		# List of bits measured by Eve in the quantum channel
eve_intercepted_bad_bit_list = []	# List of bad bits selected by Eve where Eve and Bod basis matches Alice’s
    




#####################################################
# Interactive Input Section                         #
# The following prompts collect runtime parameters: #
# - Eavesdropper presence                           #
# - Noise models (depolarization, amplitude decay)  #
# - Number of transmitted bits (N)                  #
# Default values shown in parentheses               #
#####################################################
r = input("Is there an eavesdropper on the quantum communication channel? ([y]=yes, default no) ")
there_is_an_eavesdropper = (r == "y" or r == "Y")	# Flag: Introduce an eavesdropper into the communication channel
r = input("Probability of quantum depolarization (real number, default: 0.04) ")
if is_a_real_number(r):
	r1 =  float(r)
	if r1 == 0: 
		there_is_quantum_depolarization = False	# Flag: Insert noise type 1 into the communication channel
	elif r1 > 0 and r1 <=1:
		there_is_quantum_depolarization = True	# Flag: Insert noise type 1 into the communication channel
		depolarization_probability = r1	# Depolarizing noise probability in the communication channel
	else:
		print("Input error 1!")
		quit()
else:
		there_is_quantum_depolarization = True	# Flag: Insert noise type 1 into the communication channel
		depolarization_probability = 0.04	# Depolarizing noise probability in the communication channel
r = input("Probability of quantum amplitude decay (real number, default: 0.09) ")
if is_a_real_number(r):
	r1 =  float(r)
	if r1 == 0: 
		there_is_quantum_amplitude_decay = False # Flag: Insert noise type 2 into the communication channel
	elif r1 > 0 and r1 <=1:
		there_is_quantum_amplitude_decay = True # Flag: Insert noise type 2 into the communication channel
		amplitude_decay_probability = float(r)	# Amplitude damping probability in the communication channel
	else:
		print("Input error 2!")
		quit()
else:
		there_is_quantum_amplitude_decay = True	# Flag: Insert noise type 1 into the communication channel
		amplitude_decay_probability = 0.09	# Amplitude damping probability in the communication channel
r = input("Number of transmitted bits N (positive integer, default: 100) ")
if r.isnumeric(): 
	nr_of_quantum_random_bits = int(r)	# Number of bits generated by the QRNG for the key
else:
	nr_of_quantum_random_bits = 100	# Number of bits generated by the QRNG for the key
    




#######################################################
# Loop that emulates bit-by-bit quantum transmission; #
# 1st communication phase:                            #
#######################################################
for i in range(nr_of_quantum_random_bits):
	
	# Create the quantum circuit:
	circuit = cirq.Circuit()
	
	####################
	# Alice Equipment: #
	####################
	
	# Insert Alice’s first Quantum Random Number Generator into the circuit:
	circuit.append(cirq.H(QRNGalice1))				# Insert a HADAMARD gate
	circuit.append(cirq.measure(QRNGalice1, key='QRNGalice1m'))	# Insert a MEASURE gate
	
	# Insert Alice’s second Quantum Random Number Generator into the circuit:
	circuit.append(cirq.H(QRNGalice2))				# Insert a HADAMARD gate
	circuit.append(cirq.measure(QRNGalice2, key='QRNGalice2m'))	# Insert a MEASURE gate
	
	# The first QRNG controls a NOT gate on the communication channel:
	circuit.append(cirq.X(Q__channel).with_classical_controls('QRNGalice1m'))
	
	# The second QRNG controls a HADAMARD gate on the communication channel:
	circuit.append(cirq.H(Q__channel).with_classical_controls('QRNGalice2m'))
	
	####################
	# Quantum channel: #
	####################
	
	# If required, insert noise type 1: depolarizing noise
	if there_is_quantum_depolarization:
		circuit.append(cirq.depolarize(p=depolarization_probability).on(Q__channel))
		
	# If required, insert noise type 2: amplitude damping
	if there_is_quantum_amplitude_decay:
		circuit.append(cirq.amplitude_damp(gamma=amplitude_decay_probability).on(Q__channel))
	
	####################################################################
	# If required, insert Eve’s equipment (eavesdropping/interception) #
	####################################################################
	if there_is_an_eavesdropper:
		# Insert a pseudorandom number generator for Eve:
		eve_pseudo_random_base = random.choice([0, 1])			# Select a random base for Eve
		eve_pseudo_random_base_list.append(eve_pseudo_random_base)	# Store the random basi in the list
		# If the random base is 1 apply HADAMARD - MEASURE - HADAMARD:
		# The 1st Hadamard gate is for basis change:
		if eve_pseudo_random_base == 1:		
			circuit.append(cirq.H(Q__channel))
		# In any case, apply a MEASURE gate to intercept the bit:
		circuit.append(cirq.measure(Q__channel, key=f'eve_measure'))
		# The second Hadamard gate is used to reconstruct the altered quantum state:
		if eve_pseudo_random_base == 1:
			circuit.append(cirq.H(Q__channel))	
	
	##################
	# Bob Equipment: #
	##################
	
	# Insert the third Quantum Random Number Generator for Bob into the circuit:
	circuit.append(cirq.H(QRNGbob__1))				# Insert a HADAMARD gate
	circuit.append(cirq.measure(QRNGbob__1, key='QRNGbob__1m'))	# Insert a MEASURE gate
	
	# The third QRNG controls a HADAMARD gate on the quantum communication channel:
	circuit.append(cirq.H(Q__channel).with_classical_controls('QRNGbob__1m'))	
	
	# Apply the MEASURE gate so that Bob can read the resulting bit:
	circuit.append(cirq.measure(Q__channel, key=f'bob_measure'))

	###############################
	# Quantum circuit simulation: #
	###############################
	
	simulatore = cirq.Simulator()		# Build the quantum simulator.
	risultati = simulatore.run(circuit)	# Run the quantum simulator.
	
	# Retrieve and store the measured bit values:
	alice_random_bit = int(risultati.measurements[f'QRNGalice1m'][0][0])	# Alice random bit on the communication channel.
	alice_random_bit_list.append(alice_random_bit)
	alice_random_base = int(risultati.measurements[f'QRNGalice2m'][0][0])	# Alice random base
	alice_random_base_list.append(alice_random_base)
	bob_random_base = int(risultati.measurements[f'QRNGbob__1m'][0][0])	# Bob random base
	bob_random_base_list.append(bob_random_base)
	bob_received_bit = int(risultati.measurements[f'bob_measure'][0][0])	# Bit received by Bob
	bob_received_bit_list.append(bob_received_bit)
	if there_is_an_eavesdropper:
		eve_intercepted_bit = int(risultati.measurements[f'eve_measure'][0][0])	# Eve intercepted bit
		eve_intercepted_bit_list.append(eve_intercepted_bit)
    




#############
# OUTPUT 1: #
#############
print()
if there_is_an_eavesdropper:
	print("Alice, Bob and Eve (eavesdropper) communicate on the quantum channel:")
	print(f"{'Nr':<3} {'Alice':<6} {'Alice':<5} {'Bob':<5} {'Bob':<5} {'Eve':<5}")
	print(f"{'':<3} {'bits':<6} {'base':<5} {'base':<5} {'bits':<5} {'bits':<5}")
	for i in range(nr_of_quantum_random_bits):
		if alice_random_base_list[i] == bob_random_base_list[i]:
			print(f"\033[32m{i:<3} {alice_random_bit_list[i]:<6} {alice_random_base_list[i]:<5} {bob_random_base_list[i]:<5} {bob_received_bit_list[i]:<5} {eve_intercepted_bit_list[i]:<5} - Alice and Bob matching bases.\033[0m")
		else:
			print(f"{i:<3} {alice_random_bit_list[i]:<6} {alice_random_base_list[i]:<5} {bob_random_base_list[i]:<5} {bob_received_bit_list[i]:<5} {eve_intercepted_bit_list[i]:<5}")
else:
	print("Alice and Bob communicate on the quantum channel:")
	print(f"{'Nr':<3} {'Alice':<6} {'Alice':<5} {'Bob':<5} {'Bob':<5}")
	print(f"{'':<3} {'bits':<6} {'base':<5} {'base':<5} {'bits':<5}")
	for i in range(nr_of_quantum_random_bits):
		if alice_random_base_list[i] == bob_random_base_list[i]:
			print(f"\033[32m{i:<3} {alice_random_bit_list[i]:<6} {alice_random_base_list[i]:<5} {bob_random_base_list[i]:<5} {bob_received_bit_list[i]:<5} - Alice and Bob matching bases.\033[0m")
		else:
			print(f"{i:<3} {alice_random_bit_list[i]:<6} {alice_random_base_list[i]:<5} {bob_random_base_list[i]:<5} {bob_received_bit_list[i]:<5}")
print("Alice sent",nr_of_quantum_random_bits,"random bit(s) over the quantum channel.")
if there_is_quantum_depolarization:
	print("The quantum channel is affected by quantum depolarizing noise",end=" ")
	print("- probability=",depolarization_probability)
else:
	print("The quantum channel is free of depolarizing noise.")
if there_is_quantum_amplitude_decay:
	print("The quantum channel is affected by quantum amplitude damping noise",end=" ")
	print("- probability=",amplitude_decay_probability)
else:
	print("The quantum channel is free of amplitude damping noise.")
if there_is_an_eavesdropper: 
	print("\033[31mThere is an eavesdropper on the quantum communication channel.\033[0m")
else:
	print("No eavesdropper is present on the quantum communication channel.")
print()
    




####################################################
# Loop that emulates bases comparison and sifting; #
# 2nd communication phase:                         #
####################################################
for i in range(nr_of_quantum_random_bits):
	# Bod send bob_random_base_list[] to Alice;
	# Alice compares bob_random_base_list[] with alice_random_base_list[i] and
	# send back to Bob the positions of the matching bases:
	if alice_random_base_list[i] == bob_random_base_list[i]:
		alice_matching_bases_positions.append(i)		# Matching bases position
		alice_key_bit_list.append(alice_random_bit_list[i])	# Alice key bit list
		bob_key_bit_list.append(bob_received_bit_list[i])	# Bob key bit list
		bob_key_bit_counter += 1
		if alice_random_bit_list[i] != bob_received_bit_list[i]: 
			bob_errors += 1					# Bob errors
			bob_received_bad_bit_list.append(i)
		else:
			bob_received_bad_bit_list.append("_")
	else:
		alice_key_bit_list.append('_')
		bob_key_bit_list.append('_')
    




#############
# OUTPUT 2: #
#############
print("Alice and Bob sifting:")
print("Bob sends to Alice the sequence of the random bases it used:")
for x in bob_random_base_list: print(x,end="")
print()
print("Alice sends back to Bob the positions of the bits where the bases are the same:")
for x in alice_matching_bases_positions: print(x,"",end="")
print()
print("Alice (A) and Bob (B) sifted keys \033[31m(bit errors in red)\033[0m:")
    




#########################################################
# Loop that emulates bases observation by Eve is there; #
# 3rd communication phase (partial key extraction):     #
#########################################################
if there_is_an_eavesdropper:
	for i in range(nr_of_quantum_random_bits):
		# Eve uses the same bases of Alice and Bob where they matches:
		if alice_random_base_list[i] == bob_random_base_list[i] and alice_random_base_list[i] == eve_pseudo_random_base_list[i]:
			eve_intercepted_bit_counter += 1
			eve_key_bit_list.append(eve_intercepted_bit_list[i])		# Eve key bit list
			if alice_random_bit_list[i] != eve_intercepted_bit_list[i]: 
				eve_errors += 1						# Eve errors
				eve_intercepted_bad_bit_list.append(i)
			else:
				eve_intercepted_bad_bit_list.append("_")
		else:
			eve_key_bit_list.append('_')
    




#############
# OUTPUT 3: #
#############
print("A: ",end="")
for i in range(nr_of_quantum_random_bits):
	if alice_key_bit_list[i] != "_":
		if alice_key_bit_list[i] != bob_key_bit_list[i]:
			print("\033[31m",alice_key_bit_list[i],"\033[0m",end="")
		else:
			print(alice_key_bit_list[i],end="")
print()
print("B: ",end="")
for i in range(nr_of_quantum_random_bits):
	if alice_key_bit_list[i] != "_":
		if alice_key_bit_list[i] != bob_key_bit_list[i]:
			print("\033[31m",bob_key_bit_list[i],"\033[0m",end="")
		else:
			print(bob_key_bit_list[i],end="")
print()
if there_is_an_eavesdropper:
	print("E: ",end="")
	for i in range(nr_of_quantum_random_bits):
		if alice_key_bit_list[i] != "_":
			if alice_key_bit_list[i] != bob_key_bit_list[i]:
				print("\033[31m",eve_key_bit_list[i],"\033[0m",end="")
			else:
				print(eve_key_bit_list[i],end="")
	print()
print("Alice shared",bob_key_bit_counter,"bit(s) out of",nr_of_quantum_random_bits,"bit(s) with Bob via the QKD sifting process.")
if there_is_an_eavesdropper:
	print("Eve intercepted",eve_intercepted_bit_counter,"bit(s) of the shared key.")
    




###################################################################################
# Loop emulating the error correction process between Alice and Bob, if required; #
# 4th communication phase (Key reconciliation):                                   #
###################################################################################
qber_bob = bob_errors/bob_key_bit_counter	# Evaluate Bob's quantum bit error rate 
print("Bob ERRORS=",bob_errors,"bit(s) - QBER_BOB=",qber_bob)
if qber_bob > 0.11:				# The key agreement is rejected if the QBER exceeds 0.11
	print("\033[31m",end="")
	print("Alice and Bob discard the",bob_key_bit_counter,"shared bits because the QBER is higher than 0.1",end="")
	print("\033[0m")
else:				# If the QBER remains below the threshold, the key agreement proceeds:
	if bob_errors > 0:	# If QBER > 0, perform information reconciliation on the sifted key:
		print("\033[32mAlice and Bob retain the",bob_key_bit_counter,"shared bits, but Bob needs to correct",bob_errors,"bit(s) in the following positions:\033[0m")
		for x in bob_received_bad_bit_list: 
			if x != "_": print(x,"",end="")
		print()
		print("Beginning error correction on the sifted key:")
		alice_sifted_key = [x for x in alice_key_bit_list if x != "_"]	# Get Alice's sifted key bit list
		bob_sifted_key = [x for x in bob_key_bit_list if x != "_"]	# Get Bob's sifted key bit list
		alice_key_length = len(alice_sifted_key)			# Get Alice's sifted key bit list length
		bob_key_length = len(bob_sifted_key)				# Get Bob's sifted key bit list length
		if alice_key_length != bob_key_length:				# Alice's and Bob's sifted key lengths must match
			print("ERROR: Alice's sifted key length different than Bob one:",alice_key_length,bob_key_length)
			quit()
		subkey_total_number = alice_key_length*(alice_key_length+1)//2	# Get the maximum number of triangular subkeys from the sifted key
										# the triangular number formula is the sum of the arithmetic progression: 
										# 1+2+3+...+n = n(n+1)/2
		for i in range(0,subkey_total_number):				# For each triangular subkey from longest to smallest: check for perfect match
			bob_subkey = get_sublist(bob_sifted_key, i)		# Get Bob's i-th triangular subkey
			bob_subkey_hash = myhash(bob_subkey)			# Get Bob's i-th triangular subkey hash
			alice_subkey = get_sublist(alice_sifted_key, i)		# Get Alice's i-th triangular subkey
			alice_subkey_hash = myhash(alice_subkey)		# Get Alice's i-th triangular subkey hash
			print("Bob sends to Alice the hash value:",bob_subkey_hash,"of the subkey:",i,end=" - ")
			if bob_subkey_hash == alice_subkey_hash:		# If the hashes of both subkeys are identical, the i-th subkey is error-free
				print("Alice reports a perfect subkey match; no error detected.")
				print("\033[32mFinal key agreement on subkey no.",i,":",end="")
				for x in bob_subkey:
					print(x,end="")
				print("\033[0m")
				break
			else:							# ...If the hashes do not match, Alice rejects the i-th subkey.
				print("Alice responds by rejecting the subkey!")
	else:
		print("\033[32mAlice and Bob retain the",bob_key_bit_counter,"shared bits.\033[0m")
print()
print("QUANTUM CIRCUIT:")
print(circuit)
quit()

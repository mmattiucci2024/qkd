# QKD Emulator

A Python-based emulator for **Quantum Key Distribution (QKD)**, designed to study and reproduce the main phases of a BB84-style protocol in a clear, inspectable, and experimental way.

This project was created to explore how two parties can establish a shared secret key through quantum communication and public classical post-processing, including basis comparison, sifting, QBER estimation, and error analysis. The implementation is intended both as a didactic tool and as a practical software environment for testing QKD logic step by step.

## Overview

The emulator reproduces the core workflow of a QKD session between Alice and Bob, with optional analysis of an eavesdropper scenario involving Eve.

Typical simulated phases include:

- Random bit generation by Alice
- Random basis generation by Alice and Bob
- Quantum state preparation and measurement
- Basis comparison on a public classical channel
- Sifting of the shared key
- QBER estimation
- Analysis of channel noise and/or eavesdropping effects
- Post-processing logic for key validation

The goal of the software is not to interact with real quantum hardware, but to provide a transparent and controllable environment for understanding how QKD works in practice.

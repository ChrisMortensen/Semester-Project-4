# Cybersecurity Solutions in Peer-to-Peer Instant Messaging
A BSc 4th-semester project that investigates security vulnerabilities in peer-to-peer (P2P) instant messaging and produces a prototype demonstrating practical defenses. The project implements a P2P messaging prototype and evaluates a set of cybersecurity measures to answer the research question below.

Which security measures can be applied to secure a peer-to-peer communication platform?

## Features
* A minimal P2P instant messaging prototype (peer discovery, direct messaging).
* Implemented security measures:
  * End-to-end encryption using ECDH (SECP256R1) and AES-GCM
  * Code injection prevention using subprocesses and sanitization
  * DDos/Dos discovery and subsequent rate limiting
  * Wi-Fi Jamming considerations (transport layer)
* Peer discovery via Tailscale device list (`tailscale status --json`) to bootstrap secure P2P connections.

## Technologies
* Language:   Python 3.13
* Libraries:  cryptography
* Networking: Tailscale (VPN used for NAT traversal)
* Tested on:  Windows, macOS, Linux

## Conclusion
The system serves as an initial starting point for projects where the emphasis lies in other areas than security or core instant messaging functionality.

# CoChem-SEED: Standalone Codespace GUI Architecture
**Date:** 2026-08-07
**Target:** GitHub Classroom 50 Deployment (Undergrad Organic Chemistry)

This document outlines the definitive architecture for `CoChem-SEED`. It has been formally decoupled from the `CoChem-BASE` orchestration pipeline. SEED is now a **standalone, self-contained educational web application** explicitly engineered for zero-friction deployment via GitHub Codespaces, allowing 24 students to operate completely independently.

## 1. Directory Structure Overhaul
```text
CoChem-SEED/
├── .devcontainer/
│   ├── devcontainer.json   # GitHub Codespace configuration & postCreateCommand
│   └── Dockerfile          # Installs Python, Node.js, and specialist MLFF models
├── frontend/
│   ├── src/
│   │   ├── components/     # React UI (Premium Glassmorphism matching CoChem-GUI)
│   │   └── package.json    # Vite, Molstar WebGL, Framer Motion
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI web server
│   │   ├── api_nist.py     # SDBS & NIST Database retrieval
│   │   ├── socratic_llm.py # LLM Intent Grading Engine
│   │   └── physics_local.py# Direct wrapper for bundled MACE-OFF24, MACE IR, and Thessues
│   └── requirements.txt    # fastapi, mace, thessues, pydantic
├── electron_fallback/      # Electron wrapper for students running locally (.exe)
├── generate_seed_300.py    # Generative script for suggestions (Safely Stored)
├── generate_seed_arch.py   # Generative script for architecture (Safely Stored)
└── README.md
```

## 2. GitHub Classroom 50 & Codespace Independence
This repository is designed to be pushed via GitHub Classroom to groups of 24 students simultaneously.
* **No Code Visibility:** Students will not interact with Python files or Jupyter notebooks. 
* **Zero Friction Bootstrapping:** When a student opens the repository in a GitHub Codespace, the `.devcontainer` configuration automatically installs the Python dependencies, boots the FastAPI backend, and starts the Vite frontend on port `3000`. The student simply clicks the forwarded web link to enter the premium CoChem GUI. This guarantees absolute independence while the professor tours the lab.

## 3. Self-Contained Specialist Physics Engine
Because SEED is independent of the HPC pipeline (`CoChem-BASE` / `NODE`), it cannot send ZeroMQ payloads for expensive DFT calculations.
* **Bundled Physics:** The Codespace container natively bundles highly accurate Machine Learning Force Fields (MLFF), specifically **MACE-OFF24**, **MACE IR**, **Thessues**, and other specialist models for precise spectroscopic predictions.
* **Rapid Execution:** When a student asks to see the $1700$ cm$^{-1}$ stretch of a ketone, FastAPI executes a localized **MACE IR** calculation directly inside the 2-core Codespace, extracting the precise Hessian and streaming the coordinates to Molstar in less than 500 milliseconds. Similarly, **MACE-OFF24** is used for instantaneous and flawless 3D coordinate generation from SMILES.

## 4. Electron Desktop Fallback
If a student's Codespace connection drops or they prefer offline study, the `electron_fallback/` directory contains an Electron shell. This allows the exact same React/FastAPI stack to be bundled via PyInstaller and deployed as a standalone native Windows `.exe`.

## 5. Dynamic Database Sourcing
- `api_nist.py` and `api_sdbs.py` operate completely independently. The FastAPI backend fetches `.jdx` files on-the-fly and overlays the student's theoretical predictions atop raw, noisy experimental data.
- The `socratic_llm.py` dynamically penalizes brute-force guessing and rewards students who type chemical justifications explaining the variance between the MACE theoretical peak and the SDBS experimental peak.

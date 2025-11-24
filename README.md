# **Truth-First: Unified Deepfake and Phishing Detector**

## Overview

Truth-First is a unified and privacy-focused web platform designed to help users verify suspicious digital content. It supports image and video deepfake detection, phishing URL analysis, and email fraud analysis. The platform routes each input to its appropriate detection pipeline and presents results in a simple, accessible format intended for all types of users, including beginners and digitally less experienced individuals.

This repository currently contains the project overview, design concepts, and architecture prepared for submission. Implementation will begin in later development phases.

---

## Problem Motivation

India continues to see a rapid rise in cyber fraud incidents. More than five lakh phishing cases were reported in 2024, resulting in losses above ₹22,000 crore. Deepfake misuse has grown sharply, with a 550 percent increase since 2019 and a major surge during the 2024 election cycle. These threats cause financial and reputational harm, particularly for seniors, small businesses, and rural or digitally illiterate users who lack verification tools.

There is currently no accessible platform that can check multiple forms of suspicious content in one place.

---

## What Truth-First Aims to Do

Truth-First is designed to analyse four major threat categories:

* Deepfake images
* Deepfake short videos
* Phishing URLs
* Email-based scams or social engineering attempts

The platform focuses on clear results, transparency, multilingual accessibility, and privacy-conscious processing. It also generates a pre-filled NCRP complaint template to make cybercrime reporting easier.

---

## Key Features

* A single platform for detecting images, videos, URLs, and email content
* Detection logic adapted for Indian threat patterns, including .in domain phishing and local deepfake misuse
* Simple and mobile-friendly interface suitable for all users
* Clear explanations that do not require technical knowledge
* Privacy-first behaviour with temporary processing

---

## Demo UI (Mockup)

```
![Demo UI - Truth-First](https://github.com/raja-sec/truth-first/blob/cca103a7f52ac5d6472bd3ec441a35fa0a3ffa69/demo-ui-truth-first.png)

```

Shows the planned interface for selecting scan type and viewing recent analysis results.

---

## System Architecture (Concept)

```
![Tentative Architecture Overview](https://github.com/raja-sec/truth-first/blob/cca103a7f52ac5d6472bd3ec441a35fa0a3ffa69/Untitled%20Diagram.jpg)

```

Illustrates the overall workflow between the frontend, backend, and model pipelines.

---

## Planned Tech Stack

* Frontend: React
* Backend: FastAPI
* ML Models: EfficientNet-B0 (images), Random Forest (URLs), DistilBERT (emails), EfficientNet-GRU (videos)
* Datasets: UCI, PhishTank, Celeb-DF, FaceForensics++, READFake
* Deployment: Railway or Render

---

## Current Status

This repository includes:

* The written abstract
* Architecture overview
* Demo UI design
* Technical description and future scope

The platform is currently in the design and documentation stage.

---

## Team

Raja Mishra, Rajvi Savla

---

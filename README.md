# DAILY LIVE STUDIO

A free, PC-based helper project for looping a video to YouTube Live.

## Important architecture

- This repository contains the public information website.
- Actual RTMPS video encoding/streaming must run on the user's own PC using FFmpeg and a local companion app.
- A free static website host cannot keep an FFmpeg process running or provide a reliable 24/7 cloud stream.
- In free PC mode, the PC, local companion app, and internet connection must stay on for the entire broadcast.

## Publish the public website with GitHub Pages

1. Open **Settings → Pages** in this repository.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select branch **main** and folder **/(root)**, then Save.
4. Wait for GitHub Pages to publish the site. The public address will be shown in the Pages settings.

## Safety

Never put a YouTube stream key in this repository, website source, screenshots, or public messages. Use only videos you own or are licensed to broadcast.

## Project status

The public landing page is included. The local FFmpeg streaming companion is a separate component and must be installed and running on the streaming PC. This static page alone does not start a live broadcast.
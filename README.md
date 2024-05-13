# Overview

This repository is created for a unit called "Individual Project" (Bachelor Thesis/Dissertation).

The project involved an HCI study on the Email Inbox.

The email inbox UI is imitating the [current Gmail design](https://support.google.com/mail/answer/11555490?hl=en-GB) on purpose.

![Breach-UI](https://github.com/manami-bunbun/Individual-Project/assets/30760730/49336a86-2b02-4161-82fc-c06936c94d73)


## Study 1: 
An application for conducting a _Breaching Experiment_ 

The app is now available on [https://breach-gmail.onrender.com/](https://breach-gmail.onrender.com/) 

Experiment detail : [Google Slides](https://docs.google.com/presentation/d/1uVSxhoyy5nj9j9fo0KYhJC3riARUWyz1n1lw6keZkJc/edit?usp=sharing)


## Study 2: 
An application to evaluate _EmoGist_

The app is now available on [https://emogist.onrender.com/](https://emogist.onrender.com/) 

Experiment detail : [Google Slides](https://docs.google.com/presentation/d/1nYzvKUQFrAueB-JQdsnx6eaemDQh5uummPuQvvzz5WU/edit?usp=sharing)


# Instruction

Both apps need credentials to be issued on Google Cloud. ([Instruction](https://developers.google.com/workspace/guides/create-credentials))
The app was set to have the credential JSON file in the parent directory. 
Apps may want to access Google Auth and Gmail via this file.

Also, in Study 2, you may want to create `.env` via `.env copy` for the GPT API key. ([Instruction](https://platform.openai.com/docs/quickstart#:~:text=Account%20setup,not%20share%20it%20with%20anyone.))


## Architecture
The apps were build with FastAPI.

### Study 1
![Study1-FlowChart](https://github.com/manami-bunbun/Individual-Project/assets/30760730/5e4b12b2-694c-41f6-b185-ec77f2503fc0)

### Study 2
![Study2-FC](https://github.com/manami-bunbun/Individual-Project/assets/30760730/9b21b272-25f5-4349-9560-02ffb66658cd)

# Google Search

## Overview

The Google Search plugin uses the Google Custom Search JSON API to perform web and image searches, returning structured results. It requires a Google API Key and a Custom Search Engine ID (CX).

## Configuration

### 1. Enable the Custom Search API

Go to the [Google Cloud Console](https://console.cloud.google.com/apis/library/customsearch.googleapis.com) and enable the **Custom Search API** for your project.

### 2. Create an API Key

Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials) in the Google Cloud Console and create an API Key.

### 3. Create a Custom Search Engine

Go to the [Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all) control panel, create a new search engine, and copy the **Search Engine ID** (CX).

### 4. Get Google tools from Plugin Marketplace

The Google tools can be found at the Plugin Marketplace, please install it first.

### 5. Fill in the configuration in Dify

On the Dify navigation page, click `Tools > Google > To authorize` and fill in both the **Google API Key** and the **Custom Search Engine ID (CX)**.

### 6. Use the tool

You can use the Google tool in the following application types:

#### Chatflow / Workflow applications

Both Chatflow and Workflow applications support adding a Google tool node.

#### Agent applications

Add the Google tool in the Agent application, then enter online search instructions to call this tool.

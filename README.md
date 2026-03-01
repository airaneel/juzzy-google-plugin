# Google Search Plugin for Dify

Google Search, Image Search, and Web Crawl tools powered by the Google Custom Search API.

## Tools

- **Google Search** — web search with structured results (JSON for workflows, XML for agents)
- **Google Image Search** — image search with metadata (dimensions, thumbnails, source)
- **Web Crawl** — fetch any URL and extract clean markdown content using trafilatura

## Installation

### From GitHub

In your Dify instance, go to **Plugins > Install from GitHub** and enter this repository URL.

### Manual

1. Clone this repository
2. Package with `dify plugin package ./`
3. Upload the `.difypkg` file via **Plugins > Install from local file**

## Setup

### 1. Enable the Custom Search API

Go to the [Google Cloud Console](https://console.cloud.google.com/apis/library/customsearch.googleapis.com) and enable the **Custom Search API** for your project.

### 2. Create an API Key

Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials) and create an API Key.

### 3. Create a Custom Search Engine

Go to [Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all), create a new search engine, and copy the **Search Engine ID** (CX).

### 4. Configure in Dify

Navigate to **Tools > Google > Authorize** and enter your **Google API Key** and **Custom Search Engine ID (CX)**.

## Usage

Works in Chatflow, Workflow, and Agent applications. When using Google Search in an Agent, enable the **"Used in Agent nodes"** parameter for optimized output formatting.

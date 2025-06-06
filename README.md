# GIF Optimizer

A Nighty Selfbot script that optimizes GIFs to reduce file size using Giflossy in Docker.

## Features

- Optimize GIFs from URLs or file attachments
- Adjust compression level with the `--lossy` parameter
- Modify playback speed with the `--speed` parameter (broken dgaf to fix, setpts sucks ass)
- Persistent storage option for optimized GIFs
- Automatic upload to litterbox.catbox.moe for files that exceed the configured size limit (default 8MB)
- Speed modification to make GIFs faster or slower
- Optional detailed optimization results output

## Requirements

- Nighty Selfbot installed and configured
- Docker Desktop (Windows/Mac) or Docker (Linux)
- Two Docker images:
  - `dylanninin/giflossy:latest` - For GIF optimization
  - `jrottenberg/ffmpeg:latest` - For speed modification

## Setup

1. Install Docker from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Pull the required Docker images:
   ```bash
   docker pull dylanninin/giflossy:latest
   docker pull jrottenberg/ffmpeg:latest
   ```
3. Test the containers:
   ```bash
   docker run --rm dylanninin/giflossy gifsicle --help
   docker run --rm jrottenberg/ffmpeg ffmpeg -version
   ```
4. Install the script in your Nighty Selfbot scripts folder

## Usage

The script is designed to be used with Nighty Selfbot. Here are the main commands:

- `<p>optimize <gif_url> [--lossy=<value>] [--speed=<factor>]`
  Optimize a GIF from a URL with optional parameters

- `<p>optimize [--lossy=<value>] [--speed=<factor>]`
  Optimize an attached GIF file with optional parameters

- `<p>optimize setup`
  Show Docker setup instructions

- `<p>optimize path <download_path>`
  Set download path for optimized GIFs

- `<p>optimize debug`
  Toggle debug mode for detailed logging

- `<p>optimize persistent`
  Toggle persistent storage to keep optimized GIFs

- `<p>optimize lb <1|12|24|72>`
  Set litterbox file expiry time in hours (1, 12, 24, or 72)

- `<p>optimize limit <size_mb>`
  Set max file size before uploading to litterbox

- `<p>optimize results`
  Toggle detailed optimization results

- `<p>optimize status`
  Check if the Giflossy container is working properly

## Parameters

- `--lossy=<value>`: Sets the compression level (default: 30)
  - Higher values = smaller file size, with some quality loss
  - Range: typically 1-100

- `--speed=<factor>`: Sets the playback speed (default: 1.0)
  - Values > 1.0 make the GIF play faster
  - Values < 1.0 make the GIF play slower
  - Negative values make the GIF play in reverse

## Examples

```
<p>optimize https://example.com/image.gif
<p>optimize https://example.com/image.gif --lossy=50 --speed=2.0
<p>optimize --lossy=40
<p>optimize --speed=0.5
```

## How It Works

1. The script downloads the GIF from the provided URL or attachment
2. If speed modification is requested, FFmpeg is used to adjust the playback speed
3. Giflossy applies lossy compression to reduce file size
4. The optimized GIF is sent back to the Discord channel through Nighty Selfbot
5. If the file is still over the configured limit (default 8MB), it's uploaded to litterbox.catbox.moe with a time-limited link

## Default Settings

- Lossy Level: 30
- Speed Factor: 1.0
- Debug Mode: Disabled
- Persistent Storage: Disabled
- Litterbox Expiry: 24 hours
- Litterbox Size Limit: 8MB
- Detailed Results: Disabled
- Download Path: System temp directory + "gif_optimizer" subfolder

## Changelog

### v1.0.0
- Initial release

## License

MIT 
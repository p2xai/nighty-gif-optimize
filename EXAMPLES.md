# GIF Optimizer Examples for Nighty

## Basic Usage

### Optimizing a GIF from URL
```
<p>optimize https://example.com/animation.gif
```

### Optimizing an attached GIF
Upload a GIF file to Discord and add the command as the comment:
```
<p>optimize
```

## Advanced Usage

### Setting Compression Level
The `--lossy` parameter controls compression level (higher values = smaller files with more quality loss):
```
<p>optimize https://example.com/animation.gif --lossy=50
```

### Modifying Playback Speed
The `--speed` parameter adjusts playback speed (values > 1 make it faster, < 1 make it slower):
```
<p>optimize https://example.com/animation.gif --speed=2.0
```

### Slow Motion GIF
To create a slow-motion effect:
```
<p>optimize https://example.com/animation.gif --speed=0.5
```

### Reversed GIF
To play the GIF in reverse:
```
<p>optimize https://example.com/animation.gif --speed=-1.0
```

### Combining Parameters
You can combine both parameters:
```
<p>optimize https://example.com/animation.gif --lossy=40 --speed=1.5
```

## Configuration Commands

### Setting Download Path
```
<p>optimize path C:\Users\YourName\Downloads\GIFs
```

### Enabling Persistent Storage
This keeps optimized GIFs instead of removing them after sending:
```
<p>optimize persistent
```

### Setting Litterbox Expiry Time
For files that exceed Discord's 8MB limit, they're uploaded to litterbox.catbox.moe. You can set the expiry time:
```
<p>optimize lb 24
```
Valid values: 1, 12, 24, or 72 hours

### Checking Status
To verify the Docker containers are working and see current settings:
```
<p>optimize status
```

## Tips for Best Results

1. Start with the default lossy level (30) and adjust as needed
2. For larger GIFs, try higher lossy values (50-80)
3. For animations with lots of colors or details, use lower lossy values (10-30)
4. If you need to make a GIF very small, combine a high lossy value with a faster speed
5. Use the status command to verify Docker is properly configured
6. Enable persistent storage if you want to keep your optimized GIFs

## Troubleshooting

If you encounter any issues:

1. Make sure Docker is running
2. Verify the Docker images are installed with `<p>optimize status`
3. Try setting a new download path to a location you have write access to
4. Enable debug mode with `<p>optimize debug` to get more detailed logs
5. For very large GIFs, try increasing the lossy value further

## Note About Nighty Selfbot

This script is specifically designed for Nighty Selfbot and uses its command structure and script implementation. Commands are triggered using the `<p>` prefix followed by `optimize` and any additional parameters. 
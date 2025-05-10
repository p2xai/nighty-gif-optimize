@nightyScript(
    name="GIF Optimizer v1.0.0",
    author="thedorekaczynski",
    description="Optimizes GIFs to reduce file size using Giflossy in Docker",
    usage="""<p>optimize <gif_url> [--lossy=<value>] [--speed=<factor>]
<p>optimize (with attached GIF file) [--lossy=<value>] [--speed=<factor>]
<p>optimize setup (shows Docker setup instructions)
<p>optimize path <download_path>
<p>optimize debug (toggle debug mode)
<p>optimize persistent (toggle persistent storage)
<p>optimize lb <1|12|24|72> (Set litterbox expiry time in hours)
<p>optimize status"""
)
def gif_optimizer_script():
    """
    GIF OPTIMIZER
    -------------

    Optimizes GIFs to reduce file size using Giflossy in Docker.
    
    DOCKER SETUP GUIDE:
    1. Create and verify a Docker account:
       - Go to https://hub.docker.com/signup
       - This is required before you can pull Docker images
    
    2. Install Docker on your system:
       - Windows/Mac: Download Docker Desktop from docker.com
       - Linux: Install docker package
    
    3. Pull required image:
       ```bash
       docker pull dylanninin/giflossy:latest
       ```
    
    4. Test container:
       ```bash
       docker run --rm dylanninin/giflossy gifsicle --help
       ```
       If you see the help text, the container is working.
    
    SETUP:
    1. Make sure Docker is running on your system
    2. (Optional) Set a permanent download path:
       <p>optimize path C:\\Downloads\\GIFs
    3. (Optional) Enable persistent storage to keep optimized GIFs:
       <p>optimize persistent
    4. (Optional) Set litterbox file expiry time:
       <p>optimize lb <1|12|24|72>
    5. Call the command with the GIF URL and optional arguments:
       <p>optimize https://example.com/image.gif [--lossy=<value>] [--speed=<factor>]
    
    COMMANDS:
    <p>optimize <gif_url> [--lossy=<value>] [--speed=<factor>]
        Optimize GIF from URL with options:
        - lossy: Lossy compression level (default: 30, higher = smaller file)
        - speed: Playback speed factor (default: 1.0, higher = faster)
    
    <p>optimize (with attached GIF)
        Optimize attached GIF file using default settings
        You can also include the lossy and speed options with attachments
    
    <p>optimize setup
        Show Docker setup instructions
    
    <p>optimize path <download_path>
        Set download path for optimized GIFs
    
    <p>optimize debug (toggle debug mode)
        Toggle debug mode for detailed logging
    
    <p>optimize persistent (toggle persistent storage)
        Toggle persistent storage to keep optimized GIFs
    
    <p>optimize lb <1|12|24|72>
        Set litterbox file expiry time in hours
    
    <p>optimize status
        Check if Giflossy container is working
    
    DEFAULT SETTINGS:
    - Lossy Level: 30 (good balance between quality and size)
    - Speed Factor: 1.0 (normal playback speed)
    - Debug Mode: Disabled by default
    - Persistent Storage: Disabled by default
    - Litterbox Expiry: 24 hours
    - Download Path: System temp directory + "gif_optimizer" subfolder
      (When persistent storage is enabled, GIFs are stored in a "gifs" subfolder 
       along with a "workdir" subfolder for temporary files required for optimization)
    
    EXAMPLES:
    <p>optimize https://example.com/image.gif
        Optimize GIF from URL with default settings (lossy=30, speed=1.0)
    
    <p>optimize --lossy=50 --speed=2.0
        Optimize attached GIF with higher compression and 2x speed
    
    <p>optimize https://example.com/image.gif --lossy=50 --speed=0.5
        Optimize URL GIF with higher compression and 0.5x speed
    
    FILE SIZE LIMITATIONS:
    - Discord has a file size limit of 8MB for GIFs
    - If the GIF is still too large after optimization, it will be uploaded to litterbox.catbox.moe
    - For large GIFs, it's recommended to:
      1. Use a higher lossy value (e.g., --lossy=50)
    
    NOTES:
    - Requires Docker to be installed and running
    - Files are processed locally in Docker container
    - When persistent storage is enabled, GIFs are saved with unique names
      based on the original GIF filename and timestamp
    - Both URL links and direct file attachments are supported
    - Giflossy optimization can significantly reduce file size while maintaining quality
    - Large files (>8MB) are automatically uploaded to litterbox.catbox.moe
    - Speed modification is applied before optimization to ensure smooth playback
    - This script is specifically designed for Nighty Selfbot and uses its API
    """
    import aiohttp
    import asyncio
    import os
    import re
    import tempfile
    from pathlib import Path
    import shutil
    from datetime import datetime
    
    # Config keys
    DOWNLOAD_PATH_KEY = "gif_optimizer_download_path"
    DEBUG_ENABLED_KEY = "gif_optimizer_debug_enabled"
    PERSISTENT_STORAGE_KEY = "gif_optimizer_persistent_storage"
    LITTERBOX_EXPIRY_KEY = "gif_optimizer_litterbox_expiry"
    
    # Helper function for debug logging
    def debug_log(message, type_="DEBUG"):
        """Log debug messages if debug mode is enabled"""
        if getConfigData().get(DEBUG_ENABLED_KEY, False):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [GIF OPTIMIZER] [{type_}] {message}", type_=type_)
    
    # Initialize configuration
    if getConfigData().get(DOWNLOAD_PATH_KEY) is None:
        default_path = os.path.join(tempfile.gettempdir(), "gif_optimizer")
        updateConfigData(DOWNLOAD_PATH_KEY, default_path)
        debug_log(f"Initialized default download path: {default_path}", type_="INFO")
    
    if getConfigData().get(DEBUG_ENABLED_KEY) is None:
        updateConfigData(DEBUG_ENABLED_KEY, False)
        debug_log("Initialized debug mode to disabled", type_="INFO")

    if getConfigData().get(PERSISTENT_STORAGE_KEY) is None:
        updateConfigData(PERSISTENT_STORAGE_KEY, False)
        debug_log("Initialized persistent storage to disabled", type_="INFO")
        
    if getConfigData().get(LITTERBOX_EXPIRY_KEY) is None:
        updateConfigData(LITTERBOX_EXPIRY_KEY, "24h")  # Default to 24 hours
        debug_log("Initialized litterbox expiry to 24h", type_="INFO")
    
    # Helper function to ensure download directory exists
    def ensure_download_dir(persistent=False, workdir=False):
        download_path = getConfigData().get(DOWNLOAD_PATH_KEY)
        if persistent:
            download_path = os.path.join(download_path, "gifs")
            if workdir:
                download_path = os.path.join(download_path, "workdir")
        os.makedirs(download_path, exist_ok=True)
        return download_path

    # Helper function to generate unique filename
    def generate_gif_filename(url):
        # Extract filename from URL or generate timestamp-based name
        url_filename = os.path.splitext(os.path.basename(url))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean the filename to remove invalid characters
        url_filename = re.sub(r'[^\w\-_]', '_', url_filename)
        return f"{url_filename}_{timestamp}.gif"
    
    # Helper function to parse arguments
    def parse_args(args_str):
        lossy_match = re.search(r'--lossy=(\d+)', args_str)
        speed_match = re.search(r'--speed=(-?\d*\.?\d+)', args_str)  # Allow negative values
        
        # Get the URL (everything before the first flag)
        url = args_str
        for match in [lossy_match, speed_match]:
            if match and match.group(0) in url:
                url = url.replace(match.group(0), "").strip()
        
        return {
            "url": url.strip(),
            "lossy": int(lossy_match.group(1)) if lossy_match else 30,
            "speed": float(speed_match.group(1)) if speed_match else 1.0
        }
    
    # Helper function to download file
    async def download_file(url, filename):
        download_path = ensure_download_dir()
        file_path = os.path.join(download_path, filename)
        debug_log(f"Downloading to: {file_path}", type_="INFO")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                    return file_path
                else:
                    raise Exception(f"Download failed with status {response.status}")
    
    # Helper function to run docker command
    async def run_docker_cmd(cmd):
        debug_log(f"Running docker command: {cmd}", type_="DEBUG")
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Docker command failed: {stderr.decode()}")
        return stdout.decode()

    # Helper function to modify GIF speed using FFmpeg
    async def modify_gif_speed(input_path, output_path, speed_factor):
        """Modify GIF speed using FFmpeg"""
        debug_log(f"Modifying GIF speed with factor: {speed_factor}", type_="INFO")
        
        # Create temporary paths for intermediate files
        temp_dir = os.path.dirname(input_path)
        temp_video = os.path.join(temp_dir, "temp_video.mp4")
        temp_gif = os.path.join(temp_dir, "temp_gif.gif")
        
        try:
            # Step 1: Convert GIF to video
            ffmpeg_cmd = (
                f'docker run --rm -v "{temp_dir}:/src" -v "{temp_dir}:/dest" jrottenberg/ffmpeg '
                f'-y -i /src/{os.path.basename(input_path)} '
                f'-c:v libx264 -pix_fmt yuv420p '
                f'/dest/temp_video.mp4'
            )
            await run_docker_cmd(ffmpeg_cmd)
            
            # Step 2: Apply speed modification
            if speed_factor < 0:
                speed_factor = abs(speed_factor)
                ffmpeg_cmd = (
                    f'docker run --rm -v "{temp_dir}:/src" -v "{temp_dir}:/dest" jrottenberg/ffmpeg '
                    f'-y -i /src/temp_video.mp4 '
                    f'-vf "reverse,setpts={1/speed_factor}*PTS" '
                    f'-c:v libx264 -pix_fmt yuv420p '
                    f'/dest/temp_video.mp4'
                )
            else:
                ffmpeg_cmd = (
                    f'docker run --rm -v "{temp_dir}:/src" -v "{temp_dir}:/dest" jrottenberg/ffmpeg '
                    f'-y -i /src/temp_video.mp4 '
                    f'-vf "setpts={1/speed_factor}*PTS" '
                    f'-c:v libx264 -pix_fmt yuv420p '
                    f'/dest/temp_video.mp4'
                )
            await run_docker_cmd(ffmpeg_cmd)
            
            # Step 3: Convert back to GIF
            ffmpeg_cmd = (
                f'docker run --rm -v "{temp_dir}:/src" -v "{temp_dir}:/dest" jrottenberg/ffmpeg '
                f'-y -i /src/temp_video.mp4 '
                f'-vf "fps=10,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" '
                f'/dest/temp_gif.gif'
            )
            await run_docker_cmd(ffmpeg_cmd)
            
            # Step 4: Move the result to the output path
            shutil.move(temp_gif, output_path)
            
            # Clean up temporary files
            try:
                os.remove(temp_video)
            except:
                pass
            
            debug_log(f"Speed modification completed: {output_path}", type_="INFO")
            return True
            
        except Exception as e:
            debug_log(f"Speed modification failed: {str(e)}", type_="ERROR")
            # Clean up temporary files in case of error
            try:
                if os.path.exists(temp_video):
                    os.remove(temp_video)
                if os.path.exists(temp_gif):
                    os.remove(temp_gif)
            except:
                pass
            raise

    # Helper function to upload files to litterbox.catbox.moe
    async def upload_to_litterbox(file_path):
        """Upload a file to litterbox.catbox.moe and return the URL.
        
        The uploaded file will be available for the configured duration before expiration.
        This is used as a fallback when files are too large for Discord's 8MB limit.
        """
        debug_log(f"Uploading file to litterbox.catbox.moe: {file_path}", type_="INFO")
        
        try:
            # Read the file content first
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            async with aiohttp.ClientSession() as session:
                # Prepare the file for upload
                data = aiohttp.FormData()
                data.add_field('fileToUpload', file_content, filename=os.path.basename(file_path))
                data.add_field('reqtype', 'fileupload')
                data.add_field('time', getConfigData().get(LITTERBOX_EXPIRY_KEY, "24h"))  # Use configured expiry time
                
                # Upload the file
                async with session.post('https://litterbox.catbox.moe/resources/internals/api.php', data=data) as response:
                    if response.status == 200:
                        url = await response.text()
                        if url.startswith('https://'):
                            debug_log(f"File uploaded successfully: {url}", type_="INFO")
                            return url
                        else:
                            raise Exception(f"Invalid response from litterbox: {url}")
                    else:
                        raise Exception(f"Failed to upload file: HTTP {response.status}")
        except Exception as e:
            debug_log(f"Error uploading to litterbox: {str(e)}", type_="ERROR")
            raise

    @bot.command(name="optimize", description="Optimize GIF to reduce file size using Giflossy")
    async def optimize_command(ctx, *, args: str = ""):
        await ctx.message.delete()
        
        # Handle debug command
        if args.lower() == "debug":
            current_debug = getConfigData().get(DEBUG_ENABLED_KEY, False)
            new_debug = not current_debug
            updateConfigData(DEBUG_ENABLED_KEY, new_debug)
            status = "enabled" if new_debug else "disabled"
            debug_log(f"Debug mode {status}", type_="INFO")
            await ctx.send(f"✅ Debug mode {status}")
            return
            
        # Handle setup command
        if args.lower() == "setup":
            setup_text = (
                "**Giflossy Docker Setup Guide**\n\n"
                "1. Create and verify a Docker account:\n"
                "   - Go to https://hub.docker.com/signup\n"
                "   - This is required before you can pull Docker images\n\n"
                "2. Install Docker:\n"
                "   - Windows/Mac: Download Docker Desktop from docker.com\n"
                "   - Linux: Install docker package\n\n"
                "3. Pull required images:\n"
                "   ```bash\n"
                "   docker pull dylanninin/giflossy:latest\n"
                "   docker pull jrottenberg/ffmpeg:latest\n"
                "   ```\n\n"
                "4. Test containers:\n"
                "   ```bash\n"
                "   docker run --rm dylanninin/giflossy gifsicle --help\n"
                "   docker run --rm jrottenberg/ffmpeg ffmpeg -version\n"
                "   ```\n"
                "   If you see the help text, the containers are working.\n\n"
                "5. Optional settings:\n"
                "   - Set download path: `<p>optimize path <path>`\n"
                "   - Enable persistent storage: `<p>optimize persistent`\n"
                "   - Set litterbox expiry time: `<p>optimize lb <1|12|24|72>`\n\n"
                "6. Start optimizing:\n"
                "   ```\n"
                "   <p>optimize <gif_url> [--lossy=<value>] [--speed=<factor>]\n"
                "   ```"
            )
            msg = await ctx.send(setup_text)
            await asyncio.sleep(30)
            await msg.delete()
            return
            
        # Handle path command
        if args.lower().startswith("path "):
            path = args[5:].strip()
            try:
                os.makedirs(path, exist_ok=True)
                updateConfigData(DOWNLOAD_PATH_KEY, path)
                debug_log(f"Download path updated to: {path}", type_="INFO")
                await ctx.send(f"✅ Download path set to: {path}")
            except Exception as e:
                debug_log(f"Error setting path: {str(e)}", type_="ERROR")
                await ctx.send(f"❌ Error setting path: {str(e)}")
            return
            
        # Handle status command
        if args.lower() == "status":
            msg = await ctx.send("🔍 Checking Giflossy configuration...")
            try:
                # Get current configuration
                download_path = getConfigData().get(DOWNLOAD_PATH_KEY)
                debug_enabled = getConfigData().get(DEBUG_ENABLED_KEY, False)
                persistent_enabled = getConfigData().get(PERSISTENT_STORAGE_KEY, False)
                
                # Test giflossy
                giflossy_version = await run_docker_cmd("docker run --rm dylanninin/giflossy gifsicle --version")
                # Clean up the version output to remove warranty text
                giflossy_version = giflossy_version.split('\n')[0]  # Get just the first line
                giflossy_version = giflossy_version.strip()  # Remove newlines
                
                # Check if download path exists and is writable
                path_exists = os.path.exists(download_path)
                path_writable = os.access(download_path, os.W_OK) if path_exists else False
                
                # Create status message content
                status_content = (
                    f"**🎨 Docker Giflossy**: ✅ Working\n"
                    f"```{giflossy_version}```\n"
                    f"**📁 Download Path**:\n"
                    f"```{download_path}```\n"
                    f"**🔍 Path Status**: {'✅' if path_exists else '❌'} Exists, {'✅' if path_writable else '❌'} Writable\n\n"
                    f"**⚙️ Features**:\n"
                    f"{'✅' if debug_enabled else '❌'} 🐛 Debug Mode\n"
                    f"{'✅' if persistent_enabled else '❌'} Persistent Storage\n"
                    f"**📤 Litterbox**: {getConfigData().get(LITTERBOX_EXPIRY_KEY, '24h')} expiry\n\n"
                    f"**📊 Default Settings**:\n"
                    f"• 🔧 Lossy Level: 30\n"
                    f"• 🕒 Speed Factor: 1.0\n"
                    f"• 💾 Storage: gifs subfolder when persistent\n"
                    f"• 🕒 Litterbox Expiry: {getConfigData().get(LITTERBOX_EXPIRY_KEY, '24h')}"
                )
                
                # Save current private setting and temporarily disable it
                current_private = getConfigData().get("private")
                updateConfigData("private", False)
                
                # Send embed
                await forwardEmbedMethod(
                    channel_id=ctx.channel.id,
                    content=status_content,
                    title="GIF Optimizer Status"
                )
                
                # Restore original private setting
                updateConfigData("private", current_private)
                
                debug_log("Status check successful", type_="INFO")
                await msg.delete()
            except Exception as e:
                error_msg = f"❌ Error checking status: {str(e)}"
                debug_log(error_msg, type_="ERROR")
                await msg.edit(content=error_msg)
            return

        # Handle persistent storage command
        if args.lower() == "persistent":
            current_persistent = getConfigData().get(PERSISTENT_STORAGE_KEY, False)
            new_persistent = not current_persistent
            updateConfigData(PERSISTENT_STORAGE_KEY, new_persistent)
            status = "enabled" if new_persistent else "disabled"
            debug_log(f"Persistent storage {status}", type_="INFO")
            await ctx.send(f"✅ Persistent storage {status}")
            return
            
        # Handle litterbox command
        if args.lower().startswith("lb "):
            time = args[3:].strip().lower()
            valid_times = {"1": "1h", "12": "12h", "24": "24h", "72": "72h"}
            if time in valid_times:
                updateConfigData(LITTERBOX_EXPIRY_KEY, valid_times[time])
                debug_log(f"Litterbox expiry time updated to: {valid_times[time]}", type_="INFO")
                await ctx.send(f"✅ Litterbox file expiry set to {valid_times[time]}")
            else:
                debug_log(f"Invalid litterbox time attempted: {time}", type_="ERROR")
                await ctx.send("❌ Invalid time. Use 1, 12, 24, or 72 hours")
            return
        
        # Parse arguments for optimization
        parsed_args = parse_args(args)
        gif_url = parsed_args["url"]
        lossy_value = parsed_args["lossy"]
        speed_factor = parsed_args["speed"]
        
        # Check for file attachment
        if ctx.message.attachments:
            if len(ctx.message.attachments) > 1:
                await ctx.send("❌ Please attach only one GIF file")
                return
            attachment = ctx.message.attachments[0]
            gif_url = attachment.url
            debug_log(f"Using attached file: {attachment.filename}", type_="INFO")
        elif not gif_url:
            await ctx.send("❌ Please provide a GIF URL or attach a GIF file")
            return
        
        msg = await ctx.send("⏳ Processing GIF...")
        
        try:
            # Clean up any existing files first
            work_dir = ensure_download_dir(persistent=True, workdir=True)
            output_dir = ensure_download_dir(persistent=True)
            debug_log(f"Work directory: {work_dir}", type_="DEBUG")
            debug_log(f"Output directory: {output_dir}", type_="DEBUG")
            
            for file in ["input.gif", "speed_modified.gif", "optimized.gif"]:
                try:
                    os.remove(os.path.join(work_dir, file))
                    debug_log(f"Cleaned up existing file: {file}", type_="INFO")
                except:
                    pass
            
            # Download GIF
            await msg.edit(content="⏳ Downloading GIF...")
            gif_path = os.path.join(work_dir, "input.gif")
            async with aiohttp.ClientSession() as session:
                async with session.get(gif_url) as response:
                    if response.status == 200:
                        with open(gif_path, 'wb') as f:
                            while True:
                                chunk = await response.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                        debug_log(f"Downloaded GIF to: {gif_path}", type_="INFO")
                    else:
                        raise Exception(f"Download failed with status {response.status}")
            
            # Verify input file exists
            if not os.path.exists(gif_path):
                raise Exception("Input GIF file not found after download")
            
            # Generate unique filename based on original filename or URL
            original_filename = ""
            if ctx.message.attachments:
                original_filename = os.path.splitext(ctx.message.attachments[0].filename)[0]
            else:
                original_filename = os.path.splitext(os.path.basename(gif_url))[0]
            
            # Clean filename and add timestamp
            original_filename = re.sub(r'[^\w\-_]', '_', original_filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            optimized_filename = f"{original_filename}_{timestamp}_optimized.gif"
            
            # Store original size before optimization
            original_size = os.path.getsize(gif_path) / (1024 * 1024)  # Convert to MB
            debug_log(f"Original GIF size: {original_size:.2f}MB", type_="INFO")
            
            # Modify speed if specified
            if speed_factor != 1.0:
                await msg.edit(content=f"⏳ Modifying GIF speed to {speed_factor}x...")
                speed_modified_gif = os.path.join(work_dir, "speed_modified.gif")
                await modify_gif_speed(gif_path, speed_modified_gif, speed_factor)
                gif_path = speed_modified_gif  # Use speed-modified GIF for optimization
            
            # Optimize with Giflossy
            await msg.edit(content=f"⏳ Optimizing GIF with lossy={lossy_value}...")
            optimized_gif = os.path.join(work_dir, "optimized.gif")
            giflossy_cmd = (
                f'docker run --rm -v "{work_dir}:/src" -v "{work_dir}:/dest" dylanninin/giflossy '
                f'gifsicle --lossy={lossy_value} /src/{os.path.basename(gif_path)} -o /dest/optimized.gif'
            )
            debug_log(f"Giflossy command: {giflossy_cmd}", type_="DEBUG")
            await run_docker_cmd(giflossy_cmd)
            
            if os.path.exists(optimized_gif):
                # Check file size
                optimized_size = os.path.getsize(optimized_gif) / (1024 * 1024)  # Convert to MB
                debug_log(f"Optimized GIF size: {optimized_size:.2f}MB", type_="INFO")
                
                # Calculate size reduction percentage
                size_reduction = ((original_size - optimized_size) / original_size) * 100
                debug_log(f"Size reduction: {size_reduction:.1f}%", type_="INFO")
                
                # If still over 8MB, try one more time with higher lossy value
                if optimized_size > 8 and lossy_value < 50:
                    debug_log("GIF still too large, trying again with higher lossy value", type_="INFO")
                    giflossy_cmd = (
                        f'docker run --rm -v "{work_dir}:/src" -v "{work_dir}:/dest" dylanninin/giflossy '
                        f'gifsicle --lossy=50 /src/{os.path.basename(gif_path)} -o /dest/optimized.gif'
                    )
                    debug_log(f"Second Giflossy command: {giflossy_cmd}", type_="DEBUG")
                    await run_docker_cmd(giflossy_cmd)
                    
                    # Check size again
                    if os.path.exists(optimized_gif):
                        optimized_size = os.path.getsize(optimized_gif) / (1024 * 1024)
                        debug_log(f"Second optimization size: {optimized_size:.2f}MB", type_="INFO")
                        
                        # Recalculate size reduction percentage
                        size_reduction = ((original_size - optimized_size) / original_size) * 100
                        debug_log(f"Size reduction after second attempt: {size_reduction:.1f}%", type_="INFO")
                        
                        if optimized_size > 8:
                            debug_log("GIF still too large after second optimization", type_="WARNING")
                            # Move optimized file to output directory
                            output_path = os.path.join(output_dir, optimized_filename)
                            shutil.move(optimized_gif, output_path)
                            await msg.edit(content="⏳ File size exceeds Discord's 8MB limit. Uploading to litterbox...")
                            try:
                                litterbox_url = await upload_to_litterbox(output_path)
                                await ctx.send(
                                    f"**📊 Optimization Results**\n"
                                    f"• Original Size: {original_size:.2f}MB\n"
                                    f"• Optimized Size: {optimized_size:.2f}MB\n"
                                    f"• Size Reduction: {size_reduction:.1f}%\n"
                                    f"• Lossy Level: {lossy_value}\n"
                                    f"• Speed Factor: {speed_factor}\n\n"
                                    f"**📤 File Upload**\n"
                                    f"• Status: ✅ Uploaded to litterbox\n"
                                    f"• URL: {litterbox_url}\n"
                                    f"• Expires: {getConfigData().get(LITTERBOX_EXPIRY_KEY, '24h')}\n\n"
                                    f"⚠️ Note: File exceeds Discord's 8MB limit"
                                )
                                await msg.delete()
                            except Exception as upload_error:
                                await msg.edit(content=f"❌ Failed to upload to litterbox: {str(upload_error)}")
                            return
                        else:
                            # Move optimized file to output directory
                            output_path = os.path.join(output_dir, optimized_filename)
                            shutil.move(optimized_gif, output_path)
                            debug_log("GIF optimized successfully on second attempt", type_="INFO")
                    else:
                        debug_log("Second optimization failed", type_="WARNING")
                        await ctx.send("⚠️ GIF optimization failed. Please try again.")
                        await msg.delete()
                        return
                else:
                    # Move optimized file to output directory
                    output_path = os.path.join(output_dir, optimized_filename)
                    shutil.move(optimized_gif, output_path)
                    debug_log("GIF optimized successfully", type_="INFO")
            else:
                debug_log("GIF optimization failed", type_="WARNING")
                await ctx.send("⚠️ GIF optimization failed. Please try again.")
                await msg.delete()
                return
            
            # Check final file size before sending
            final_size = os.path.getsize(output_path) / (1024 * 1024)  # Convert to MB
            if final_size > 8:
                await msg.edit(content="⏳ File size exceeds Discord's 8MB limit. Uploading to litterbox.catbox.moe...")
                try:
                    litterbox_url = await upload_to_litterbox(output_path)
                    await ctx.send(
                        f"**📊 Optimization Results**\n"
                        f"• Original Size: {original_size:.2f}MB\n"
                        f"• Optimized Size: {final_size:.2f}MB\n"
                        f"• Size Reduction: {size_reduction:.1f}%\n"
                        f"• Lossy Level: {lossy_value}\n"
                        f"• Speed Factor: {speed_factor}\n\n"
                        f"**📤 File Upload**\n"
                        f"• Status: ✅ Uploaded to litterbox\n"
                        f"• URL: {litterbox_url}\n"
                        f"• Expires: {getConfigData().get(LITTERBOX_EXPIRY_KEY, '24h')}\n\n"
                        f"⚠️ Note: File exceeds Discord's 8MB limit"
                    )
                    await msg.delete()
                except Exception as upload_error:
                    await msg.edit(content=f"❌ Failed to upload to litterbox: {str(upload_error)}")
                return
                
            # Send the optimized GIF
            await msg.edit(content="⏳ Sending optimized GIF...")
            
            # Calculate and display size reduction
            size_reduction = ((original_size - final_size) / original_size) * 100
            await ctx.send(f"GIF Size: {final_size:.2f}MB (Reduced by {size_reduction:.1f}%) [Lossy: {lossy_value}, Speed: {speed_factor}]", file=discord.File(output_path))
                
            await msg.delete()
            
            # Clean up workdir
            try:
                debug_log("Cleaning up temporary files", type_="INFO")
                for file in ["input.gif"]:
                    try:
                        os.remove(os.path.join(work_dir, file))
                        debug_log(f"Cleaned up work file: {file}", type_="INFO")
                    except:
                        pass
                debug_log(f"Kept optimized GIF file in persistent storage: {output_path}", type_="INFO")
            except Exception as e:
                debug_log(f"Cleanup error: {str(e)}", type_="WARNING")
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            debug_log(error_msg, type_="ERROR")
            await msg.edit(content=error_msg)

# Initialize the script
gif_optimizer_script() 
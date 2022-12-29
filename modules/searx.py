import asyncio
import sys
import os
import msg
import yaml

async def exec(program: str, args: list[str]) -> None:
    log_error = ""
    proc = await asyncio.create_subprocess_exec(
        program,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    while True:
        if proc.stdout.at_eof() and proc.stderr.at_eof():
            break

        stderr = (await proc.stderr.readline()).decode()
        if stderr:
            log_error = log_error + "\n" + stderr

        await asyncio.sleep(0.01)

    await proc.communicate()

    if proc.returncode == 0:
        msg.info(f'{program} {" ".join(args)} exited with {proc.returncode}')
    else:
        msg.fatal_error(f'{program} {" ".join(args)} exited with {proc.returncode}\n\n\033[90m<<<LOG(stderr)>>> {log_error}')

# Config SearXNG
msg.info("Configuring SearXNG configuration file...")

with open("/etc/searxng/settings.yml", "r+") as f:
  searxng_config = yaml.safe_load(f)
  
  i = 0
  while True:
    try:
        searxng_config["outgoing"]["proxies"]["all://"][i] = os.environ[f'FREA_PROXY_{i}']
        msg.info(f"Use proxy {i} ({os.environ[f'FREA_PROXY_{i}']})")
    except:
        # Do not use proxy
        if i == 0:
            msg.warn("Do not use proxy")
            try:
                del searxng_config["outgoing"]["proxies"]
            except:
                pass

        del i
        break

    else:
        i += 1

  yaml.dump(searxng_config, f)


# Start SearXNG
os.chdir('searxng/src')
del searxng_config


if os.system('sed -i "s/ultrasecretkey/$(openssl rand -hex 32)/g" /etc/searxng/settings.yml') != 0:
    msg.fatal_error(f"Failed to generate SearXNG secret.")
    sys.exit(1)

asyncio.run(exec('python3', ['searx/webapp.py']))

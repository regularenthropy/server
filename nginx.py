import asyncio
import sys
import msg

async def exec(program: str, args: list[str]) -> None:
    proc = await asyncio.create_subprocess_exec(
        program,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    while True:
        if proc.stdout.at_eof() and proc.stderr.at_eof():
            break

        stdout = (await proc.stdout.readline()).decode()
        if stdout:
            msg.info(f'{stdout}')

        stderr = (await proc.stderr.readline()).decode()
        if stderr:
            msg.error(f'{stderr}')

        await asyncio.sleep(0.01)

    await proc.communicate()

    if proc.returncode == 0:
        msg.info(f'{program} {" ".join(args)} exited with {proc.returncode}')
    else:
        msg.fatal_error(f'{program} {" ".join(args)} exited with {proc.returncode}')

asyncio.run(exec('nginx', ['-g', 'daemon off;']))
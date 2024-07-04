import argparse
import asyncio
from dataclasses import dataclass, field
from io import BytesIO
from typing import Optional

import aiohttp
from aiohttp.client_exceptions import ClientError, ClientResponseError
from async_limiter import Limiter
from tqdm import tqdm

urls = [
    "https://habr.com/ru/companies/brave/articles/795125/",
    "https://habr.com/ru/companies/brave/articles/787448/",
    "https://habr.com/ru/companies/brave/articles/773012/",
    "https://habr.com/ru/companies/brave/news/704430/",
    "https://habr.com/ru/companies/brave/news/584434/",
    "https://habr.com/ru/companies/brave/articles/788748/",
    "https://habr.com/ru/companies/brave/articles/799833/",
    "https://habr.com/ru/companies/brave/news/579456/",
    "https://habr.com/ru/news/599589/",
    "https://habr.com/ru/companies/brave/articles/790550/",
    "https://habr.com/ru/companies/brave/news/762890/",
    "https://habr.com/ru/news/766182/",
    "https://habr.com/ru/news/589681/",
    "https://habr.com/ru/news/787962/",
    "https://habr.com/ru/news/564176/",
    "https://habr.com/ru/news/732380/",
    "https://habr.com/ru/news/797373/",
    # "https://habr.com/ru/companies/brave/articles/788742/",
    # "https://habr.com/ru/cmpanies/brave/rticles/788742/",
    "https://habr.com/ru/news/769156/",
    "https://habr.com/ru/companies/brave/news/711480/",
    "https://habr.com/ru/companies/brave/articles/795125/",
    "https://habr.com/ru/companies/brave/articles/787448/",
    "https://habr.com/ru/companies/brave/articles/773012/",
    "https://habr.com/ru/companies/brave/news/704430/",
    "https://habr.com/ru/companies/brave/news/584434/",
    "https://habr.com/ru/companies/brave/articles/788748/",
    "https://habr.com/ru/companies/brave/articles/799833/",
    "https://habr.com/ru/companies/brave/news/579456/",
    "https://habr.com/ru/news/599589/",
    "https://habr.com/ru/companies/brave/articles/790550/",
    "https://habr.com/ru/companies/brave/news/762890/",
    "https://habr.com/ru/news/766182/",
    "https://habr.com/ru/news/589681/",
    "https://habr.com/ru/news/787962/",
    "https://habr.com/ru/news/564176/",
    "https://habr.com/ru/news/732380/",
    "https://habr.com/ru/news/797373/",
    # "https://habr.com/ru/companies/brave/articles/788742/",
    # "https://habr.com/ru/cmpanies/brave/rticles/788742/",
    "https://habr.com/ru/news/769156/",
    "https://habr.com/ru/companies/brave/news/711480/",
    "https://habr.com/ru/companies/brave/news/711480/",
    "https://habr.com/ru/companies/brave/news/711480/",
    "https://habr.com/ru/companies/brave/articles/795125/",
    "https://habr.com/ru/companies/brave/articles/787448/",
    "https://habr.com/ru/companies/brave/articles/773012/",
    "https://habr.com/ru/companies/brave/news/704430/",
    "https://habr.com/ru/companies/brave/news/584434/",
    "https://habr.com/ru/companies/brave/articles/788748/",
    "https://habr.com/ru/companies/brave/articles/799833/",
    "https://habr.com/ru/companies/brave/news/579456/",
    "https://habr.com/ru/news/599589/",
    "https://habr.com/ru/companies/brave/articles/790550/",
    "https://habr.com/ru/companies/brave/news/762890/",
    "https://habr.com/ru/news/766182/",
    "https://habr.com/ru/news/589681/",
    "https://habr.com/ru/news/787962/",
    "https://habr.com/ru/news/564176/",
    "https://habr.com/ru/news/732380/",
    "https://habr.com/ru/news/797373/",
    # "https://habr.com/ru/companies/brave/articles/788742/",
    # "https://habr.com/ru/cmpanies/brave/rticles/788742/",
    "https://habr.com/ru/news/769156/",
    "https://habr.com/ru/companies/brave/news/711480/",
    "https://habr.com/ru/companies/brave/articles/795125/",
    "https://habr.com/ru/companies/brave/articles/787448/",
    "https://habr.com/ru/companies/brave/articles/773012/",
    "https://habr.com/ru/companies/brave/news/704430/",
    "https://habr.com/ru/companies/brave/news/584434/",
    "https://habr.com/ru/companies/brave/articles/788748/",
    "https://habr.com/ru/companies/brave/articles/799833/",
    "https://habr.com/ru/companies/brave/news/579456/",
    "https://habr.com/ru/news/599589/",
    "https://habr.com/ru/companies/brave/articles/790550/",
    "https://habr.com/ru/companies/brave/news/762890/",
    "https://habr.com/ru/news/766182/",
    "https://habr.com/ru/news/589681/",
    "https://habr.com/ru/news/787962/",
    "https://habr.com/ru/news/564176/",
    "https://habr.com/ru/news/732380/",
    "https://habr.com/ru/news/797373/",
    # "https://habr.com/ru/companies/brave/articles/788742/",
    # "https://habr.com/ru/cmpanies/brave/rticles/788742/",
    "https://habr.com/ru/news/769156/",
    "https://habr.com/ru/companies/brave/news/711480/",
    "https://habr.com/ru/companies/brave/news/711480/",
    "https://habr.com/ru/companies/brave/news/711480/",
]


@dataclass()
class Job(object):
    url: str
    retries: int = 3
    result: dict = field(default_factory=dict)
    str_result: str = ""
    buf: Optional[BytesIO] = None
    error: Optional[Exception] = None


async def main(args):
    session = aiohttp.ClientSession()
    try:
        queue_in_links = asyncio.Queue()
        queue_out_bytesio = asyncio.Queue()
        limiter = Limiter(10, 1)
        tasks = [
            asyncio.create_task(
                worker(
                    f"Worker-{i + 1}",
                    session,
                    queue_in_links,
                    queue_out_bytesio,
                    limiter,
                )
            )
            for i in range(args.num_workers)
        ]

        for url in urls:
            await queue_in_links.put(Job(url))

        bar = tqdm(
            total=len(urls),
            desc="Process urls",
            position=0,
            dynamic_ncols=True,
            leave=True,
            # bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            colour="green",
        )
        errors_bar = tqdm(
            total=len(urls),
            desc="Errors  urls",
            position=1,
            dynamic_ncols=True,
            leave=True,
            # bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            colour="red",
        )
        count_processed = 0
        while True:
            out = await queue_out_bytesio.get()
            if not isinstance(out, Job):
                continue
            queue_out_bytesio.task_done()
            count_processed += 1
            if out.error:
                errors_bar.update()
            else:
                bar.update()
            if count_processed >= bar.total:
                break

        bar.close()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    finally:
        await session.close()


async def worker(
    worker_id: str,
    session: aiohttp.ClientSession,
    queue_in: asyncio.Queue,
    queue_out: asyncio.Queue,
    limiter: Limiter,
):
    # print(f"[{worker_id} starting]")
    while True:
        job = await queue_in.get()
        try:
            if not job:
                await queue_out.put(None)
                continue
            if not isinstance(job, Job):
                raise TypeError
            url = job.url

            async with limiter:
                async with session.get(url) as response:
                    response.raise_for_status()
                    buf: BytesIO = BytesIO()
                    buf.write(await response.read())
                    # курсор буфера обязательно сбросить в ноль
                    buf.seek(0)
                    job.buf = buf
                    out_job = Job(url=job.url, buf=buf)
                    await queue_out.put(out_job)
        except (ClientResponseError, ClientError) as e:
            job.retries -= 1
            job.error = e
            if job.retries > 0:
                await queue_in.put(job)
            else:
                await queue_out.put(job)
        finally:
            queue_in.task_done()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--num-workers", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main(parse_args()))

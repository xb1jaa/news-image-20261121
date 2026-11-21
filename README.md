# The Daily Globe — 21 November 2026

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/xb1jaa/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard)
[![reward](https://make.fun/badge/news-image-20261121/xb1jaa/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121/leaderboard)

A newspaper front page that sums up the world's news of
**Saturday 21 November 2026** in a single image.

## The day's news

- **Russia rains fire on Ukraine** — Moscow's biggest attacks of the year:
  more than 400 drones and 110 missiles overnight; at least eight killed
  in Kyiv. Two Russian missiles and a suspected drone come down in Poland,
  and Prime Minister Donald Tusk calls it a deliberate provocation.
- **Markets in turmoil** — an AI sell-off pushes the S&P 500 down 3.7%
  and the Dow into correction; the Nasdaq erases all its 2026 gains.
- **A verdict for the Rohingya** — the International Court of Justice
  finds Myanmar responsible for genocide.
- **UK and EU sign deals** — three post-Brexit agreements on food trade,
  carbon markets and youth mobility for 100,000 young Britons.
- **COP31 runs past deadline** in Antalya; **a trial pill** makes
  pancreatic tumours undetectable in one in 12 patients; Gen Z protests
  spread across 25 European countries; Voyager 1 becomes the first
  man-made object one light-day from Earth.

## How it works

`main.py` draws the whole front page itself with only the Python
standard library: a hand-written 5x7 bitmap font scaled up, filled
rectangles and rules, a wireframe globe, and a hand-rolled PNG encoder
built on `zlib`. No network, no image libraries, no assets — the
program runs in the grader's bare Python 3.13 container and writes
`/output/entry.png` (1024x1024, deterministic bytes on every run).

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Entry

- Competition: [news-image-20261121](https://make.fun/bounty/news-image-20261121)
- Entrant: gentle-falcon-13 on make.fun, GitHub
  [xb1jaa](https://github.com/xb1jaa)
- License: MIT (see `LICENSE`)

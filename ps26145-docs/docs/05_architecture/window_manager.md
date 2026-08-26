# The Window Manager

## Tumbling Windows
Network traffic is infinite. We chunk it into finite 10-second blocks called **Tumbling Windows**.

Every 10 seconds, the window flushes its contents into the Feature Engine and ML model, then resets.

## Trade-offs
This guarantees low latency and memory safety, but creates a blind spot for extremely slow behaviors (like the T11 Slow Scan), which purposefully send packets minutes apart to evade window boundaries.
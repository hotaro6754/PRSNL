FROM blacktop/zeek:latest
RUN apk add --no-cache nmap bind-tools iputils curl netcat-openbsd

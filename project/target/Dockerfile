FROM alpine:latest
RUN apk add --update --no-cache openssh python3
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
RUN adduser -h /home/pi -s /bin/sh -D pi
RUN echo -n 'pi:sunshine' | chpasswd
ENTRYPOINT ["/entrypoint.sh"]
EXPOSE 22
COPY entrypoint.sh /